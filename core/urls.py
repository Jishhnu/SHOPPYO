from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("register/",views.Customer_Register,name="Customer_Register"),
    path("",views.Login,name="login"),
    path("Customer_Logout/", views.Customer_Logout, name="customer_logout"),
    path("Customer_Home/",views.Customer_Home,name="customer_home"),
    path("customer_dashboard/", views.Customer_Dashboard, name="customer_dashboard"),
    path("customer_update/", views.Customer_Update, name="customer_update"),
    path("customer_address/", views.Customer_Address, name="customer_address"),
]