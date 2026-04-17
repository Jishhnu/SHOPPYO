from django.contrib import admin
from django.urls import path
from seller import views

urlpatterns = [
    path("seller_register/",views.Seller_Register,name="Seller_Register"),
    # path("seller_onboarding/",views.seller_onboarding,name="seller_onboarding"),
    path("seller_home/",views.seller_home,name="seller_home"),
    path("seller_waiting/",views.seller_waiting,name="seller_waiting"),
    path("seller_logout/", views.seller_logout, name="seller_logout"),

#-------------Seller_Dashboard-------------------------
    path("seller_dashboard/",views.Seller_Dashboard,name="seller_dashboard"),
    path("seller_profile/",views.seller_profile,name="seller_profile"),
    path("seller_editprofile/",views.seller_editprofile,name="seller_editprofile"),

#-------------Product_Inventory--------------------------
    path("product_inventory/",views.product_inventory,name="product_inventory"),
    path("seller_add_products/",views.seller_add_products,name="seller_add_products"),
    path('get-subcategories/',views.get_subcategories, name='get_subcategories'),

    path('product/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:id>/', views.delete_product, name='delete_product'),

#-------------Seller_Orders------------------------------
    path("seller_order/",views.seller_order,name="seller_order"),
    path('order/cancel/<int:order_id>/', views.seller_cancel_order, name='seller_cancel_order'),
    path('seller/order_details/<int:order_id>/', views.seller_order_details, name='seller_order_details'),

#--------------Seller_Review-----------------------------
    path("seller_review/",views.seller_review,name="seller_review"),
    path('seller/reply-review/<int:review_id>/', views.seller_reply_review, name='seller_reply_review'),
]
