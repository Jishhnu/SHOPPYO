from django.contrib import admin
from django.urls import path
from adminapk import views

urlpatterns = [
    path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),
    path("admin_logout/", views.admin_logout, name="admin_logout"),

#---------Category-----------------------
    path("admin_category/",views.admin_category,name="admin_category"),
    path('toggle-category/<int:id>/', views.toggle_category, name='toggle_category'),

#---------Sub_Category-----------------------    
    path("admin_subcategory/<slug:slug>/",views.admin_subcategory,name="admin_subcategory"),
    path('admin_subcategory/toggle-subcategory/<int:id>/', views.toggle_subcategory),
    path("delete_subcategory/<slug:slug>/",views.delete_admin_subcategory,name="delete_admin_subcategory"),

#---------SellerVerification----------------------
    path("admin_sellerverification/",views.admin_sellerverification,name='admin_sellerverification'),

#----------admin_approvedsellers-------------------
    path("admin_approvedsellers/",views.admin_approvedsellers,name='admin_approvedsellers'),

#----------admin_rejectsellers-------------------
    path("admin_rejectsellers/",views.admin_rejectsellers,name='admin_rejectsellers'),

#----------admin_suspendedsellers-------------------
    path("admin_suspendedsellers/",views.admin_suspendedsellers,name='admin_suspendedsellers'),

#----------admin_productverification-------------------
    path("admin_productverification/",views.admin_productverification,name='admin_productverification'),

#----------admin_approvalproduct-------------------
    path("admin_approvedproduct/",views.admin_approvedproduct,name='admin_approvedproduct'),

#----------admin_rejectproduct-------------------
    path("admin_rejectproduct/",views.admin_rejectproduct,name='admin_rejectproduct'),

#----------admin_users-------------------
    path("admin_users/",views.admin_users,name='admin_users'),
    path('user-toggle/<int:id>/<str:action>/', views.user_toggle, name='user_toggle'),

#----------admin_orders-------------------
    path("admin_orders/",views.admin_orders,name='admin_orders'),
    path("admin_order_detail/<int:id>/",views.admin_order_detail,name='admin_order_detail'),

]