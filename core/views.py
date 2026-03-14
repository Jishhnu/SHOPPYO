from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from seller.models import *
from customer.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
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
        
        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email.strip().lower(),
            email=email,
            password=password,
            )
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
    return render(request,"customer/Custm_Register.html")


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
            
        else:
            messages.error(request,"Invalid Email or Password")
            return render(request,"customer/login.html")
    return render(request,"core/login.html")

@login_required
def Customer_Home(request):
    user=request.user
    product=Product.objects.filter(is_active=True)
    category=Category.objects.filter(is_active=True)
    try:
        cart=Cart.objects.get(user=user)
        cart_count=cart.items.count()
    except Cart.DoesNotExist:
        cart_count=0
    return render(request,"customer/customer_home.html", {"profile_user":user,"products":product,"categories":category,"cart_count":cart_count})


@login_required
def category(request):
    category=Category.objects.all()
    return render(request,'core/category.html',{'category':category})

@login_required
def sub_category(request,slug):
    category=get_object_or_404(Category,slug=slug)
    sub_category=SubCategory.objects.filter(category=category)
    all_category=Category.objects.all()
    return render(request,'core/sub_category.html',{'sub_category':sub_category,'all_category':all_category})

@login_required
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