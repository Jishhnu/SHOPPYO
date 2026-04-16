from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
# from django.http import HttpResponse
from core.models import *
from customer.models import *
from .models import *
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from core.decorator import approved_seller_required, seller_required

from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.db.models import Avg, Sum, Count, Min
from django.utils import timezone

# Create your views here.
#--------------Seller_Register--------------------------
def Seller_Register(request):
    if request.method=="POST":
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email").strip().lower()
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")
        store_name = request.POST.get("store_name")

        if password!=confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("seller_register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("seller_register")
        
        user=User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=email.strip().lower(),
            email=email,
            password=password,
            role="SELLER"
            )
        SellerProfile.objects.create(
            user=user,
            store_name=store_name
        )
        messages.success(request, "Seller account Created Successfully")
        return redirect("login")
    return render(request, "seller/Seller_Register.html")


#--------------Seller_Home--------------------------
def seller_home(request):
    return render(request, "seller/seller_home.html")


@seller_required
def seller_waiting(request):
    seller = getattr(request.user, "seller_profile", None)
    status = seller.status if seller else "PENDING"
    return render(request, "seller/seller_waiting.html", {"seller": seller, "status": status})


@seller_required
def seller_logout(request):
    logout(request)
    messages.success(request, "Seller logged out successfully")
    return redirect("login")


#--------------Seller_Dashboard--------------------------
@approved_seller_required
def Seller_Dashboard(request):
    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller)
    # orders = Order.objects.filter(items__seller=seller)

    #---Total_Revenue/Active_orders------
    total_revenue = Order.objects.filter(items__seller=seller,order_status='DELIVERED').aggregate(total=Sum('total_amount'))['total'] or 0
    active_orders = Order.objects.filter(items__seller=seller,order_status='PLACED').distinct().count()

    #----Review/Low stock--------
    reviews = Review.objects.filter(product__seller=seller)
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating = round(avg_rating, 1)

    low_stock_products = products.annotate(min_stock=Min('variants__stock_quantity')).filter(min_stock__lt=100).order_by('min_stock')[:4]

    #-----Recent_Order---------
    recent_orders=Order.objects.filter(items__seller=seller).distinct().order_by('-ordered_at')[:4]


    return render(request, "seller/Seller_dashboard.html",{'store_name': seller.store_name,'total_revenue': total_revenue,'active_orders': active_orders,
                                                        'avg_rating': avg_rating,'low_stock_products': low_stock_products,'recent_orders': recent_orders,})

#------------Seller_Profile-------------------------
@approved_seller_required
def seller_profile(request):
    user=request.user
    seller = request.user.seller_profile
    return render(request, "seller/seller_profile.html", {"seller": seller,"user": user})

@approved_seller_required
def seller_editprofile(request):
    user = request.user
    seller = user.seller_profile

    if request.method == "POST":

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.phone_number = request.POST.get("phone_number")

        if request.FILES.get("profile_image"):
            user.profile_image = request.FILES.get("profile_image")

        user.save()

        seller.store_name = request.POST.get("store_name")
        seller.gst_number = request.POST.get("gst_number")
        seller.business_address = request.POST.get("business_address")
        seller.bank_account_number = request.POST.get("bank_account_number")
        seller.ifsc_code = request.POST.get("ifsc_code")

        seller.save()

        messages.success(request, "Profile updated successfully")
        return redirect("seller_profile")
    return render(request, "seller/seller_editprofile.html",{"user": user,"seller": seller})

#-------------Product_Inventory--------------------------
@approved_seller_required
def product_inventory(request):
    try:
        seller = request.user.seller_profile
    except:
        return HttpResponse("Seller profile not found")
    
    status = request.GET.get('status')
    query = request.GET.get('search')

    products = Product.objects.filter(seller=seller).prefetch_related('variants__images').order_by('-created_at')

    #------Page-Filter-------------
    if status == "active":
        products = products.filter(approval_status="APPROVED")
    elif status == "pending":
        products = products.filter(approval_status="PENDING")
    elif status == "rejected":
        products = products.filter(approval_status="REJECTED")

    #------Search-------------
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(model_number__icontains=query)
        )

    return render(request, "seller/product_inventory.html", {"products": products,'current_status': status})

#-------------seller_Add_Products/Delete_Product--------------------------
@approved_seller_required
def seller_add_products(request):

    if request.method == 'POST':
        try:
            seller = request.user.seller_profile

            product = Product.objects.create(
                seller=seller,
                subcategory_id=request.POST.get('subcategory'),
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                brand=request.POST.get('brand'),
                model_number=request.POST.get('model_number'),
                is_cancellable=request.POST.get('is_cancellable') == 'on',
                is_returnable=request.POST.get('is_returnable') == 'on',
                return_days=int(request.POST.get('return_days') if request.POST.get('return_days') else 7)
            )
            variant = ProductVariant.objects.create(
                product=product,
                sku_code=request.POST.get('sku_code'),
                mrp=request.POST.get('mrp') if request.POST.get('mrp') else 0,
                selling_price=request.POST.get('selling_price') if request.POST.get('selling_price') else 0,
                cost_price=request.POST.get('cost_price') if request.POST.get('cost_price') else 0,
                stock_quantity=request.POST.get('stock_quantity') if request.POST.get('stock_quantity') else 0,
                weight=request.POST.get('weight') if request.POST.get('weight') else 0,
                length=request.POST.get('length') if request.POST.get('length') else 0,
                width=request.POST.get('width') if request.POST.get('width') else 0,
                height=request.POST.get('height') if request.POST.get('height') else 0,
                tax_percentage=request.POST.get('tax_percentage') if request.POST.get('tax_percentage') else 0
            )

            images = request.FILES.getlist('product_images')
            primary_index = request.POST.get('primary_index')

            for i, img in enumerate(images):

                if primary_index:
                    is_primary = (str(i) == primary_index)
                else:
                    is_primary = (i == 0)

                ProductImage.objects.create(variant=variant,image=img,is_primary=is_primary)

            messages.success(request, "Product added successfully!")
            return redirect('product_inventory')
        
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect('seller_add_products')

    categories = Category.objects.all()
    return render(request, "seller/seller_add_products.html", {'categories': categories})

@approved_seller_required
def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id)

    data = [
        {'id': sub.id, 'name': sub.name}
        for sub in subcategories
    ]

    return JsonResponse(data, safe=False)

@approved_seller_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user.seller_profile)
    product.delete()
    return redirect('product_inventory')

#-------------Edit_Product--------------------------
@approved_seller_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user.seller_profile)
    variant = product.variants.first()
    # variant = get_object_or_404(product=product)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category=product.subcategory.category)

    if request.method == "POST":

        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.brand = request.POST.get('brand')
        product.model_number = request.POST.get('model_number')
        product.subcategory_id = request.POST.get('subcategory')
        product.is_cancellable = request.POST.get('is_cancellable') == 'on'
        product.is_returnable = request.POST.get('is_returnable') == 'on'
        product.return_days = int(request.POST.get('return_days') if request.POST.get('return_days') else 7)
        product.save()

        variant.mrp = request.POST.get('mrp') or 0
        variant.selling_price = request.POST.get('selling_price') or 0
        variant.cost_price = request.POST.get('cost_price') or 0
        variant.stock_quantity = request.POST.get('stock_quantity') or 0
        variant.sku_code = request.POST.get('sku_code')
        variant.tax_percentage = request.POST.get('tax_percentage') or 0
        variant.weight = request.POST.get('weight') or 0
        variant.length = request.POST.get('length') or 0
        variant.width = request.POST.get('width') or 0
        variant.height = request.POST.get('height') or 0
        variant.save()

        images = request.FILES.getlist('product_images')
        primary_index = request.POST.get('primary_index')

        ProductImage.objects.filter(variant=variant).update(is_primary=False)       #remove old primary and update

        for i, img in enumerate(images):      #add new images
            ProductImage.objects.create(
                variant=variant,
                image=img,
                is_primary=(str(i) == primary_index)
            )

        if primary_index and primary_index.startswith("existing_"):         #Existing primary image
            img_id = primary_index.split("_")[1]
            ProductImage.objects.filter(id=img_id).update(is_primary=True)

        messages.success(request, "Product updated successfully!")
        status = request.GET.get('status')
        url = reverse('product_inventory')
        if status:
            url += f'?status={status}'
        return redirect(url)

    return render(request, 'seller/seller_update_product.html', {'product': product,'variant': variant,'categories': categories,'subcategories': subcategories})


# -----------Seller_Order---------------
@approved_seller_required
def seller_order(request):
    seller=request.user.seller_profile
    # orders=Order.objects.filter(items__seller=seller).order_by('-ordered_at')
    orders = Order.objects.filter(items__seller=seller).prefetch_related('items__variant__images').order_by('-ordered_at')

    #-------Filter-----------------
    status = request.GET.get('status')

    if status == "pending":
        orders = orders.filter(order_status="PLACED")
    elif status == "shipped":
        orders = orders.filter(order_status="SHIPPED")
    elif status == "delivered":
        orders = orders.filter(order_status="DELIVERED")
    elif status == "cancelled":
        orders = orders.filter(order_status="CANCELLED")

    #-----Search-----------
    query = request.GET.get('search')

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(user__username__icontains=query)|
            Q(address__city__icontains=query)
        )
    return render(request,"seller/seller_order.html",{'orders':orders})

@approved_seller_required
def seller_cancel_order(request,order_id):

    order=get_object_or_404(Order,id=order_id)

    if order.order_status=='PLACED':
        order.order_status='CANCELLED'
        order.save()
    return redirect('seller_order')

@approved_seller_required
def seller_order_details(request,order_id):
    orders=get_object_or_404(Order,id=order_id)

    if request.method == "POST":
        status = request.POST.get('status')

        if status == "pending":
            orders.order_status = "PLACED"

        elif status == "shipped":
            orders.order_status = "SHIPPED"

        elif status == "delivered":
            orders.order_status = "DELIVERED"

        elif status == "cancelled":
            orders.order_status = "CANCELLED"

        orders.save()
        
    return render(request,"seller/seller_order_details.html",{'order':orders})

#--------------Seller_Review-----------------------------
@approved_seller_required
def seller_review(request):
    seller=request.user.seller_profile
    products=Product.objects.filter(seller=seller).prefetch_related('reviews')
    reviews = Review.objects.filter(product__in=products).order_by('-created_at')

    total_reviews_count = reviews.count()

    #------Avg_Rating------------
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    #----Positive Feedback(rating >= 4)--------
    positive_reviews = reviews.filter(rating__gte=4).count()
    positive_percentage = int((positive_reviews / total_reviews_count) * 100) if total_reviews_count else 0

    #-------Filter--------------------
    rating = request.GET.get('rating')

    if rating == "5":
        reviews = reviews.filter(rating=5)
    elif rating == "4":
        reviews = reviews.filter(rating=4)
    elif rating == "low":
        reviews = reviews.filter(rating__lte=3)

    return render(request,"seller/seller_reviews.html",{'products': products,'reviews': reviews,'total_reviews_count': total_reviews_count,'avg_rating': round(avg_rating, 1),'positive_percentage': positive_percentage,})

    #---------seller_reply_review----------------------
@approved_seller_required
def seller_reply_review(request,review_id):
    seller=request.user.seller_profile

    review=get_object_or_404(Review,id=review_id,product__seller=seller)
    if request.method == "POST":
        reply=request.POST.get("reply_text")
        review.seller_reply=reply
        review.replied_at = timezone.now()
        review.save()

        return redirect("seller_review")
    return render(request, "seller/seller_reply_review.html", {"review": review})
