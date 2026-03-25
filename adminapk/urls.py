from django.contrib import admin
from django.urls import path
from adminapk import views

urlpatterns = [
    path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),

#---------Category-----------------------
    path("admin_category/",views.admin_category,name="admin_category"),
    path('toggle-category/<int:id>/', views.toggle_category, name='toggle_category'),

#---------Sub_Category-----------------------    
    path("admin_subcategory/<slug:slug>/",views.admin_subcategory,name="admin_subcategory"),
    path('admin/toggle-subcategory/<int:id>/', views.toggle_subcategory, name='toggle_subcategory')


]