from django.shortcuts import render,redirect,HttpResponse
# from django.http import HttpResponse
from core.models import User,Category,SubCategory
from .models import SellerProfile,Product
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from core.decorator import seller_required

# Create your views here.
# --------------Seller_Register--------------------------
def Seller_Register(request):
    if request.method=="POST":
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email").strip().lower()
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")

        if password!=confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("seller_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("seller_register")
        
        user=User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email.strip().lower(),
            email=email,
            password=password,
            role="SELLER"
            )
        messages.success(request, "Seller account Created Successfully")
        return redirect("login")
    return render(request, "seller/Seller_Register.html")

# --------------Seller_Home--------------------------
def seller_home(request):
    return render(request, "seller/seller_home.html")

# --------------Seller_Dashboard--------------------------
@seller_required
@login_required
def Seller_Dashboard(request):
    seller_profile=SellerProfile.objects.all()
    return render(request, "seller/Seller_dashboard.html", {"seller_profile": seller_profile})


