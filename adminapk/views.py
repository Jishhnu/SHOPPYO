from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from core.models import *
from seller.models import *
from customer.models import *
from django.contrib import messages 
from django.db.models import Count

from django.http import JsonResponse
import json

# Create your views here.
def admin_dashboard(request):
    return render(request,"adminapk/admin_dashboard.html")

#---------Category-----------------------
def admin_category(request):
    category=Category.objects.all().annotate( subcategory_count=Count('subcategories')).order_by('-created_at')
    if request.method=="POST":
        name= request.POST.get("name")
        slug= request.POST.get("slug")
        description= request.POST.get("description")
        # image= request.FILES.get('image')
        # image2= request.FILES.get('image2')
        image_url = request.POST.get('image_url')
        image_url2 = request.POST.get('image_url2')

        if Category.objects.filter(slug=slug).exists():
            messages.error(request,"Slug already exists!")
            return redirect('admin_category')
        
        Category.objects.create(
            name=name,
            slug=slug,
            description=description,
            image_url=image_url,
            image_url2=image_url2,
        )

        messages.success(request,"Category Added Successfully!")
        return redirect('admin_category')
    return render(request,'adminapk/admin_category.html',{'all_category':category})

def toggle_category(request, id):
    if request.method == "POST":
        category = Category.objects.get(id=id)

        data = json.loads(request.body)
        category.is_active = data.get('is_active')
        category.save()

        return JsonResponse({'status': 'success'})
    
#---------Sub_Category-----------------------
def admin_subcategory(request,slug):
    category=get_object_or_404(Category, slug=slug)
    subcategory=SubCategory.objects.filter(category=category).annotate(product_count=Count('products'))
    return render(request,'adminapk/admin_subcategory.html',{"subcategory":subcategory,"category":category})

def toggle_subcategory(request, id):
    if request.method == "POST":
        data = json.loads(request.body)

        sub = SubCategory.objects.get(id=id)
        sub.is_active = data.get("is_active")
        sub.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})