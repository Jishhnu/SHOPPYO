from django.contrib import admin
from django.urls import path
from seller import views

urlpatterns = [
    path("seller_register/",views.Seller_Register,name="Seller_Register"),
    path("seller_dashboard/",views.Seller_Dashboard,name="seller_dashboard"),
    path("seller_home/",views.seller_home,name="seller_home"),
]