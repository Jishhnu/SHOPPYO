from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/",views.Customer_Register,name="Customer_Register"),
    path("login/",views.Login_view,name="login"),

#---------------Customer_Home------------------------
    path("",views.Customer_Home,name="customer_home"),

#--------------Category/Sub_category-----------------
    path("Category/",views.category,name="category"),
    path('sub_category/<slug:slug>/',views.sub_category,name='subcategory_list'),
    path('subcategory_product/<slug:slug>/',views.subcategory_product,name='subcategory_product'),

#----------Email verification------------------------
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),

#----------Forget Password---------------------------
    path('reset-password/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html', success_url='/reset-complete/'), name='password_reset_confirm'),
    
    path('reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete')
]