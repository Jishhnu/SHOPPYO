from django.contrib import admin
from django.urls import path
from seller import views

urlpatterns = [
    path("seller_register/",views.Seller_Register,name="Seller_Register"),
    path("seller_dashboard/",views.Seller_Dashboard,name="seller_dashboard"),
    path("seller_home/",views.seller_home,name="seller_home"),

#-------------Product_Inventory--------------------------
    path("product_inventory/",views.product_inventory,name="product_inventory"),
    path("seller_add_products/",views.seller_add_products,name="seller_add_products"),

]