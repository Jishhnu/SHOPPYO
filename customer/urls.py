from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    #---------------------Dashboard/Address---------------------------------------------
    path("customer_dashboard/", views.Customer_Dashboard, name="customer_dashboard"),
    path("customer_update/", views.Customer_Update, name="customer_update"),
    path("customer_address/", views.Customer_Address, name="customer_address"),
    path("customer_address/add/", views.Customer_Address_add, name="customer_address_add"),
    path("customer_address/update/<int:address_id>/", views.Customer_Address_update, name="customer_address_update"),
    path("customer_address/default/<int:address_id>/", views.Customer_Address_set_default, name="customer_address_set_default"),
    path("Customer_Logout/", views.Customer_Logout, name="customer_logout"),

    #------------------------Cart----------------------------------------------
    path('cart/add/<int:variant_id>/', views.Add_to_cart, name='add_to_cart'),
    path('cart/', views.View_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:item_id>/', views.cart_increase, name='cart_increase'),
    path('cart/decrease/<int:item_id>/', views.cart_decrease, name='cart_decrease'),

    # ---------------Wishlist----------------------------------
    path("add-wishlist/<int:variant_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/", views.wishlist_view, name="wishlist_view"),
    path("remove-wishlist/<int:item_id>/", views.remove_from_wishlist, name="remove_wishlist"),
    path("move-to-cart/<int:item_id>/", views.move_to_cart, name="move_to_cart"),
    path("move-all-to-cart/", views.move_all_to_cart, name="move_all_to_cart"),

    #-------------Product_variant----------------------
    path("single_product_variant/<str:slug>/", views.single_product_variant, name="single_product_variant"),

    #------------------Order---------------------------
    path("order/<int:id>/",views.order,name='order'),
    path("order/select-address/<int:address_id>/",views.order_select_address,name='order_select_address'),
    path("order/place/", views.place_order, name='place_order'),
    path("order/checkout/<int:cart_id>",views.checkout,name="checkout"),
    path("order/confirmation/<int:order_id>/",views.order_confirmation,name="order_confirmation"),
    path("customer/order_history/",views.order_history,name="order_history"),
    path("reorder/<int:order_id>/",views.reorder,name="reorder"),

    #------------------Search---------------------
    path("search/",views.search,name="search"),
    path("live-search/", views.live_search, name="live_search"),

    #------------------Review--------------------
    path("add_review/<int:product_id>",views.add_review,name="add_review"),

]
