from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from seller.models import *
from customer.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .utils import generate_otp

from datetime import timedelta
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator


#Create your views here.
#_____________________________Register_________________________________________
def Customer_Register(request):
    if request.method=="POST":
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email").strip().lower()
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")

        if password!=confirm_password:
            messages.error(request, "Passwords do not Match")
            return redirect("Customer_Register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already Exists")
            return redirect("Customer_Register")
        
        user=User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email.strip().lower(),
            email=email,
            password=password,
            )
        
        user.is_active= False

        otp=generate_otp()
        # user.otp= make_password(otp) # otp hash cheyuthu vechu
        user.otp_created_at= timezone.now() #ippozhathe Timezone set akki vech user table lle
        user.save()
        print(otp)

        send_mail(
            'Your OTP code',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
        )

        request.session['email']= email
        messages.success(request, "OTP sent to your email")
        return redirect('verify_otp')
        
        # messages.success(request, "Account created successfully! Please login.")
        # return redirect('login')
    return render(request,"customer/Custm_Register.html")

def verify_otp(request):
    if request.method=="POST":
        entered_otp= request.POST.get('otp')
        email=request.session.get('email')
        if not email:
            messages.error(request, "Session expired")
            return redirect('Customer_Register')
        
        user=User.objects.get(email=email)

        if user.otp_created_at + timedelta(minutes=1) < timezone.now():
            messages.error(request,"OTP is not valid")
            return redirect('verify_otp')
        
        # if check_password(entered_otp, user.otp):
        if entered_otp == user.otp:
            user.is_active= True    # OTP verify cheyuthu ennit Active True akki
            user.otp= None
            user.otp_created_at= None
            user.save()

            del request.session['email'] #email delete cheyaan vendi browser nne OTP success ayaal

            messages.success(request, "Account verified & Created Successfully!")
            return redirect('login')
        messages.error(request,"Invalid OTP")

    return render(request,"core/verify_otp.html")

def resend_otp(request):
    email= request.session.get('email')
    if not email:
        messages.error(request, "Session expired")
        return redirect('Customer_Register')
    
    user= User.objects.get(email=email)

    if user.otp_created_at and user.otp_created_at + timedelta(seconds=30) > timezone.now():
        messages.error(request, "Wait 30 seconds before resend")
        return redirect('verify_otp')
    
    otp=generate_otp()
    user.otp= make_password(otp)
    user.otp_created_at= timezone.now()
    user.save()

    send_mail(
        'Resent OTP',
        f'Your new OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
    )

    messages.success(request,"New OTP sent")
    return render(request,"core/verify_otp.html")


#___________________Login________________________________________
def Login_view(request):
    if request.method=="POST":
        email=request.POST.get("email").strip().lower()
        password=request.POST.get("password")

        user=authenticate(request,username=email,password=password)

        if user is not None:
            login(request,user)
            # messages.success(request,'Login Successfully')

            if user.role == "CUSTOMER":
                return redirect("customer_home")
        
            elif user.role == "SELLER":
                return redirect("seller_dashboard")
            
            elif user.role == "ADMIN":
                return redirect("admin_dashboard")
            
        else:
            messages.error(request,"Invalid Email or Password")
            return redirect("login")
    return render(request,"core/login.html")

#__________________Page(Home/category/subcategory/subcategory_product)____________________________________
def Customer_Home(request):
    user=request.user
    product=Product.objects.filter(is_active=True, variants__isnull=False).distinct().prefetch_related('variants', 'variants__images')
    category=Category.objects.filter(is_active=True)
    cart_count=0
    if user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_count=cart.items.count()

    paginator = Paginator(product, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"customer/customer_home.html", {"profile_user":user,"page_obj":page_obj,"categories":category,"cart_count":cart_count})

def category(request):
    category=Category.objects.all()
    return render(request,'core/category.html',{'category':category})

def sub_category(request,slug):
    category=get_object_or_404(Category,slug=slug)
    sub_category=SubCategory.objects.filter(category=category)
    all_category=Category.objects.all()
    return render(request,'core/sub_category.html',{'sub_category':sub_category,'all_category':all_category,"category":category})

def subcategory_product(request,slug):
    sub_category=get_object_or_404(SubCategory,slug=slug)
    product=Product.objects.filter(subcategory=sub_category)
    productvariant=ProductVariant.objects.filter(product__in=product).prefetch_related('images')

    brand=request.GET.getlist('brand')
    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')
    # rating=request.GET.get('rating')

    if brand:
        productvariant=productvariant.filter(product__brand__in=brand)
    if min_price and min_price.strip():
        productvariant=productvariant.filter(selling_price__gte=min_price)
    if max_price and max_price.strip():
        productvariant=productvariant.filter(selling_price__lte=max_price)

    return render(request,'core/subcategory_products.html',{'productvariant':productvariant})