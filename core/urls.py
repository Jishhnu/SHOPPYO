from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("register/",views.Customer_Register,name="Customer_Register"),
    path("login/",views.Login_view,name="login"),
    path("",views.Customer_Home,name="customer_home"),
    path("Category/",views.category,name="category"),
    path('sub_category/<slug:slug>/',views.sub_category,name='subcategory_list'),
    path('subcategory_product/<slug:slug>/',views.subcategory_product,name='subcategory_product'),

    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
]