from django.contrib import admin
from django.urls import path
from adminapk import views

urlpatterns = [
    path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),
]