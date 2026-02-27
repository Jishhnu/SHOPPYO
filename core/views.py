from django.shortcuts import render,redirect
from .models import User, Address
from seller.models import SellerProfile,Product
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
            return render(request,"customer/Custm_Register.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already Exists")
            return render(request,"customer/Custm_Register.html")
        
        user=User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email,
            email=email,
            password=password,
            )
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
    return render(request,"customer/Custm_Register.html")


def Login(request):
    if request.method=="POST":
        email=request.POST.get("email").strip().lower()
        password=request.POST.get("password")

        user=authenticate(request,username=email,password=password)

        if user is not None:
            login(request,user)
            messages.success(request,'Login Successfully')

            if user.role == "CUSTOMER":
                return redirect("customer_home")
        
            elif user.role == "SELLER":
                return redirect("seller_dashboard")
            
        else:
            messages.error(request,"Invalid Email or Password")
            return render(request,"customer/login.html")
    return render(request,"customer/login.html")

@login_required
def Customer_Home(request):
    user=request.user
    return render(request,"customer/customer_home.html", {"profile_user":user})


@login_required
def Customer_Dashboard(request):
    user = request.user
    # # try to get user's default address, fall back to first address or None
    # default_address = Address.objects.filter(user=user, is_default=True).first()
    # if not default_address:
    #     default_address = Address.objects.filter(user=user).first()
    return render(request, "customer/customer_dashboard.html", {"profile_user": user})


@login_required
def Customer_Update(request):
    user=request.user

    if request.method=="POST":
        user.first_name=request.POST.get("first_name")
        user.last_name=request.POST.get("last_name")
        user.phone_number=request.POST.get("phone_number")
        new_email = request.POST.get("email")

        if request.FILES.get("profile_image"):
            user.profile_image = request.FILES.get("profile_image")

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "Email already exists!")
            return redirect("customer_update")
        else:
            user.email = new_email   # update current user's email

        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("customer_dashboard")
    return render(request, "customer/customer_update.html", {"profile_user": user})

@login_required
def Customer_Logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

@login_required
def Customer_Address(request):
    return render(request, "customer/customer_address.html")