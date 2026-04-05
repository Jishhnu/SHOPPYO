from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from core.models import *
from seller.models import *
from customer.models import *
from django.contrib import messages 
from django.contrib.auth import logout
from django.db.models import Count

from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

# Create your views here.
#---------Dashboard-----------------------
def admin_dashboard(request):
    pendingsellers= SellerProfile.objects.filter(status='PENDING')
    approvedsellers=SellerProfile.objects.filter(status='APPROVED')
    users=User.objects.filter(role='CUSTOMER')
    totalusers=User.objects.all().order_by('-updated_at')[:4]
    pendingproducts=Product.objects.filter(approval_status='PENDING')[:2]
    totalpendingproducts=Product.objects.filter(approval_status='PENDING')

    if request.method=="POST":
        action=request.POST.get('action')
        product_id=request.POST.get('product_id')

        product=get_object_or_404(Product, id=product_id)

        if product.approval_status == "PENDING":
            if action == "approve":
                product.approval_status = "APPROVED"
                product.is_active = True

            elif action == "reject":
                product.approval_status = "REJECTED"
                product.is_active = False

        product.save()
        return redirect("admin_dashboard")
    
    #------Total Revenue------------
    total_revenue=Order.objects.filter(order_status='DELIVERED').aggregate(total=Sum('total_amount'))['total'] or 0

    #-----Flow Chart------------
    today=timezone.now().date()
    date=[]
    daily_revenue=[]

        #------last-7days--------
    for i in range(6,-1,-1):
        day= today-timedelta(days=i)
        total= Order.objects.filter(ordered_at__date=day,order_status__in=('DELIVERED','PLACED')).aggregate(total=Sum('total_amount'))['total'] or 0
        date.append(day.strftime("%b %d"))
        daily_revenue.append(int(total))

    #------Last-Month------------------
    month_total= Order.objects.filter(ordered_at__month=today.month,order_status__in=('DELIVERED','PLACED')).aggregate(total=Sum('total_amount'))['total'] or 0
    days=today.day
    if days:
        avg=int(month_total/days)
    else:
        avg=0

    monthly_avg=[avg]*7

    #---------Top-Products---------------------
    top_products=(OrderItem.objects.filter(order__order_status__in=('DELIVERED','PLACED')).values('variant__product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5])
    product_name=[]
    product_sales=[]

    for p in top_products:
        product_name.append(p['variant__product__name'])
        product_sales.append(p['total_sold'])

    context={
        "pendingsellers":pendingsellers, "approvedsellers":approvedsellers, "users":users, "totalusers":totalusers, "pendingproducts":pendingproducts, "totalpendingproducts":totalpendingproducts,
        "total_revenue":total_revenue, 'date':date, 'daily_revenue':daily_revenue, 'monthly_avg':monthly_avg, 'product_name':product_name, 'product_sales':product_sales
    }
    
    return render(request,"adminapk/admin_dashboard.html", context)


def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

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
    categories = Category.objects.all()
    if request.method == "POST":
        category_id= request.POST.get('category_id')
        category1 = Category.objects.get(id=category_id)
        name= request.POST.get('name')
        slug= request.POST.get('slug')
        image_url= request.POST.get('image_url')
        
        if SubCategory.objects.filter(slug=slug).exists():
            messages.error(request,"Slug already exists!")
            return redirect('admin_subcategory',slug=category.slug)
        
        SubCategory.objects.create(
                category=category1,
                name=name,
                slug=slug,
                image_url=image_url,
        )
        messages.success(request, "Sub-category created successfully!")
        return redirect('admin_subcategory',slug=category.slug)

    return render(request,'adminapk/admin_subcategory.html',{"subcategory":subcategory,"category":category,"categories":categories})

@require_POST
def toggle_subcategory(request, id):
    try:
        data = json.loads(request.body)

        sub = SubCategory.objects.get(id=id)
        sub.is_active = bool(data.get('is_active'))
        sub.save()

        return JsonResponse({
            "success": True,
            "new_status": sub.is_active
        })

    except SubCategory.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "SubCategory not found"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })
    
def delete_admin_subcategory(request,slug):
    subcategory=get_object_or_404(SubCategory,slug=slug)
    category_slug = subcategory.category.slug
    subcategory.delete()
    return redirect("admin_subcategory",slug=category_slug)

#--------------SellerVerification----------------------------
def admin_sellerverification(request):
    sellers= SellerProfile.objects.filter(status='PENDING').order_by('-created_at')

    if request.method=="POST":
        action=request.POST.get('action')
        seller_id=request.POST.get('seller_id')

        seller=get_object_or_404(SellerProfile, id=seller_id)

        if seller.status == "PENDING":
            if action == "approve":
                seller.status = "APPROVED"
            elif action == "reject":
                seller.status = "REJECTED"

        if action == "approve_all":
            SellerProfile.objects.filter(status='PENDING').update(status='APPROVED')
            return redirect("admin_sellerverification")

        seller.save()
        return redirect("admin_sellerverification")
    
    return render(request,'adminapk/admin_sellerverification.html',{"sellers":sellers})

#------------------Approved_Sellers-----------------------
def admin_approvedsellers(request):
    sellers=SellerProfile.objects.filter(status='APPROVED').order_by('-created_at')

    if request.method=="POST":
        seller_id=request.POST.get('seller_id')
        action=request.POST.get('action')

        seller=get_object_or_404(SellerProfile,id=seller_id)

        if action =='pending':
            seller.status = "PENDING"
        elif action =='reject':
            seller.status = 'REJECTED'
        elif action =='suspend':
            seller.status = 'SUSPENDED'
            seller.suspended_until=timezone.now() + timedelta(days=7)
        seller.save()
        return redirect("admin_approvedsellers")
    
    suspended_seller=SellerProfile.objects.filter(status="SUSPENDED")
    for seller in suspended_seller:
        if seller.suspended_until and timezone.now() > seller.suspended_until:
            seller.status = "PENDING"
            seller.suspended_until = None
            seller.save()

    return render(request,'adminapk/admin_approvedsellers.html',{"sellers":sellers})

#----------admin_rejectsellers-------------------
def admin_rejectsellers(request):
    sellers=SellerProfile.objects.filter(status='REJECTED').order_by('-created_at')

    if request.method=="POST":
        seller_id=request.POST.get('seller_id')
        action=request.POST.get('action')

        seller=get_object_or_404(SellerProfile,id=seller_id)

        if action == "approve":
            seller.status = "APPROVED"
        
        seller.save()
        return redirect("admin_rejectsellers")
    return render(request,'adminapk/admin_rejectsellers.html',{"sellers":sellers})

#----------admin_suspendedsellers-------------------
def admin_suspendedsellers(request):
    sellers=SellerProfile.objects.filter(
        suspended_until__isnull=False,
        suspended_until__gt=timezone.now()
        ).order_by('-created_at')

    if request.method == "POST":
        seller_id=request.POST.get('seller_id')
        action=request.POST.get('action')

        seller=get_object_or_404(SellerProfile,id=seller_id)

        if action == "approve":
            seller.suspended_until = None
            seller.status = "APPROVED"

        elif action == 'reject':
            seller.suspended_until = None
            seller.status = 'REJECTED'

        seller.save()
        return redirect('admin_suspendedsellers')

    return render(request,'adminapk/admin_suspendedsellers.html',{"sellers":sellers})

#----------admin_productverification-------------------
def admin_productverification(request):
    products = Product.objects.filter(approval_status='PENDING').order_by('-created_at')
    if request.method=="POST":
        action=request.POST.get('action')
        product_id=request.POST.get('product_id')

        product=get_object_or_404(Product, id=product_id)

        if product.approval_status == "PENDING":
            if action == "approve":
                product.approval_status = "APPROVED"
                product.is_active = True

            elif action == "reject":
                product.approval_status = "REJECTED"
                product.is_active = False

        if action == "approve_all":
            Product.objects.filter(approval_status='PENDING').update(approval_status='APPROVED',is_active=True)
            return redirect("admin_productverification")

        product.save()
        return redirect("admin_productverification")
    
    return render(request,'adminapk/admin_productverification.html',{"products":products})

#----------admin_approvalproduct-------------------
def admin_approvedproduct(request):
    products = Product.objects.filter(approval_status='APPROVED').order_by('-created_at')

    if request.method=="POST":
        product_id=request.POST.get('product_id')
        action=request.POST.get('action')

        product=get_object_or_404(Product, id=product_id)

        if action =='pending':
            product.approval_status = "PENDING"
        elif action =='reject':
            product.approval_status = 'REJECTED'

        product.save()
        return redirect("admin_approvedproduct")

    return render(request,'adminapk/admin_approvedproduct.html',{"products":products})

#----------admin_rejectproduct-------------------
def admin_rejectproduct(request):
    products = Product.objects.filter(approval_status='REJECTED').order_by('-created_at')

    if request.method=="POST":
        product_id=request.POST.get('product.id')
        action=request.POST.get('action')

        product=get_object_or_404(Product, id=product_id)

        if action == "approve":
            product.approval_status = "APPROVED"
        
        product.save()
        return redirect("admin_rejectproduct")

    return render(request,'adminapk/admin_rejectproduct.html',{"products":products})

#----------admin_users-------------------
def admin_users(request):
    users=User.objects.filter(role='CUSTOMER').order_by('-created_at')
    return render(request,'adminapk/admin_users.html',{"users":users})

def user_toggle(request, id, action):
    user = get_object_or_404(User, id=id)

    if action == "activate":
        user.is_active = True
    elif action == "deactivate":
        user.is_active = False

    user.save()
    return redirect('admin_users')

#----------admin_orders-------------------
def admin_orders(request):
    orders=Order.objects.all().order_by('-ordered_at')
    return render(request,'adminapk/admin_orders.html',{"orders":orders})

def admin_order_detail(request,id):
    orders=get_object_or_404(Order,id=id)
    return render(request,'adminapk/admin_order_detail.html',{"order":orders})
