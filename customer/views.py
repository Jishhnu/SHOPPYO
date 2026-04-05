from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from core.models import *
from seller.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from decimal import Decimal
import uuid
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse,HttpResponse
import razorpay
from django.conf import settings


@login_required
def Customer_Dashboard(request):
    user = request.user
    recent_orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:5]
    default_address = Address.objects.filter(user=user, is_default=True).first()
    if not default_address:
        default_address = Address.objects.filter(user=user).first()
    return render(request, "customer/customer_dashboard.html", {"profile_user": user, "default_address": default_address,"recent_orders":recent_orders})


@login_required
def Customer_Update(request):
    user=request.user

    if request.method=="POST":
        user.first_name=request.POST.get("first_name")
        user.last_name=request.POST.get("last_name")
        user.phone_number=request.POST.get("phone_number")
        new_email = request.POST.get("email")

        if request.FILES.get("profile_image"):
            user.profile_image = request.FILES.get("profile_image")

        if new_email != user.email:
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, "Email already exists!")
                return redirect("customer_update")
            user.email = new_email
        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("customer_dashboard")
    return render(request, "customer/customer_update.html", {"profile_user": user})

@login_required
def Customer_Logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

#---------------------Address---------------------------------------------

@login_required
def Customer_Address(request):
    address = Address.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
    return render(request, "customer/customer_address.html", {'address': address})


@login_required
def Customer_Address_set_default(request, address_id):
    addr = Address.objects.get(id=address_id, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    addr.is_default = True
    addr.save()
    return redirect('customer_address')


@login_required
def Customer_Address_add(request):
    if request.method == "POST":
            full_name=request.POST.get("full_name")
            phone_number=request.POST.get("phone_number")
            pincode=request.POST.get("pincode")
            locality=request.POST.get("locality")
            house_info=request.POST.get("house_info")
            city=request.POST.get("city")
            state=request.POST.get("state")
            country=request.POST.get("country")
            landmark=request.POST.get("landmark")
            address_type=request.POST.get("address_type")
            is_default = request.POST.get("is_default") == "on"
            user=request.user

            if is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            Address.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                pincode=pincode,
                locality=locality,
                house_info=house_info,
                city=city,
                state=state,
                country=country,
                landmark=landmark,
                address_type=address_type,
                is_default=is_default,
                )
            return redirect('customer_address')
    return render(request, "customer/customer_addressadd.html")

def Customer_Address_update(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == "POST":
            address.full_name=request.POST.get("full_name")
            address.phone_number=request.POST.get("phone_number")
            address.pincode=request.POST.get("pincode")
            address.locality=request.POST.get("locality")
            address.house_info=request.POST.get("house_info")
            address.city=request.POST.get("city")
            address.state=request.POST.get("state")
            address.country=request.POST.get("country")
            address.landmark=request.POST.get("landmark")
            address.address_type=request.POST.get("address_type")
            is_default = request.POST.get("is_default") == "on"
            if is_default:
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            address.is_default = is_default
            address.save()
            return redirect('customer_address')
    return render(request, "customer/customer_address_update.html",{'address':address})

#------------------------Cart----------------------------------------------------

# def add_to_cart(request, variant_id):
#     variant = get_object_or_404(ProductVariant, id=variant_id)

#     cart, created = Cart.objects.get_or_create(user=request.user)

#     cart_item, item_created = CartItem.objects.get_or_create(
#         cart=cart, 
#         variant=variant,
#         defaults={'price_at_time': variant.price}
#     )
#     if not item_created:
#         cart_item.quantity += 1
#         cart_item.save()
#     return redirect('view_cart')

@login_required
def Add_to_cart(request, variant_id):
    variant=get_object_or_404(ProductVariant, id=variant_id)
    try:
        cart=Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart=Cart.objects.create(user=request.user)

    try:
        cart_item=CartItem.objects.get(cart=cart,variant=variant)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            cart=cart,
            variant=variant,
            price_at_time=variant.selling_price,
            quantity=1
        )
    return redirect('view_cart')

@login_required
def View_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item=CartItem.objects.filter(cart=cart)

    subtotal=0
    tax = 0
    grand_total = 0

    for items in cart_item:
        subtotal+=items.price_at_time * items.quantity
        tax = round(subtotal * Decimal('0.08'), 2)
        grand_total=subtotal+tax
        cart.total_amount=grand_total
        cart.save()
    return render(request,'customer/cart.html',{'items':cart_item,"subtotal":subtotal,'tax':tax,'total_amount':grand_total, 'cart': cart})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')



@login_required
def cart_increase(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def cart_decrease(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()   
    return redirect('view_cart')

# ---------------Wishlist---------------------------
@login_required
def add_to_wishlist(request,variant_id):
    variant=get_object_or_404(ProductVariant, id=variant_id)
    try:
        wishlist=Wishlist.objects.get(user=request.user, wishlist_name="My Wishlist")
    except Wishlist.DoesNotExist:
        wishlist=Wishlist.objects.create(user=request.user, wishlist_name="My Wishlist")

    try:
        wishlist_item=WishlistItem.objects.get(wishlist=wishlist,variant=variant)
    except WishlistItem.DoesNotExist:
        wishlist_item=WishlistItem.objects.create(
            wishlist=wishlist,
            variant=variant
        )
    return redirect("wishlist_view")

@login_required
def wishlist_view(request):
    try:
        wishlist=Wishlist.objects.get(user=request.user, wishlist_name="My Wishlist")
    except Wishlist.DoesNotExist:
        wishlist=Wishlist.objects.create(user=request.user, wishlist_name="My Wishlist")
    wishlist_item=WishlistItem.objects.filter(wishlist=wishlist)

    return render(request, "customer/wishlist.html", {"items": wishlist_item})

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    wishlist_item.delete()
    return redirect("wishlist_view")

@login_required
def move_to_cart(request,item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    variant=wishlist_item.variant
    current_price = variant.selling_price

    cart, created= Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": 1,
            "price_at_time":current_price
            }
    )

    if not created:
        cart_item.quantity +=1
        cart_item.save()

    wishlist_item.delete()

    return redirect("view_cart")

@login_required
def move_all_to_cart(request):
    wishlist = get_object_or_404(Wishlist, user=request.user, wishlist_name="My Wishlist")
    wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    cart= Cart.objects.get(user=request.user)

    for item in wishlist_items:
        current_price=item.variant.selling_price
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=item.variant,
            defaults={
                "quantity": 1,
                "price_at_time":current_price
                }
        )
        if not created:
            cart_item.quantity += 1
            cart_item.price_at_time=current_price
            cart_item.save()
        item.delete()

    return redirect("view_cart")


#-------------Single_Product_variant---------------------------

def single_product_variant(request,slug):
    product=get_object_or_404(Product, slug=slug)
    product_variant = ProductVariant.objects.filter(product=product).first()
    product_image=ProductImage.objects.filter(variant=product_variant)
    related_products=Product.objects.filter(subcategory=product.subcategory).exclude(id=product.id)

    if request.user.is_authenticated:
        review = Review.objects.filter(product=product,user=request.user).order_by('-created_at')
    else:
        review = Review.objects.filter(product=product).order_by('-created_at')

    return render(request,'customer/Single_variant.html',{'items':product_variant,'image':product_image,'review':review,"related_products":related_products})


#------------------Order---------------------------
@login_required
def order(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_variant = ProductVariant.objects.filter(product=product).first()
    
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
    
    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()
    
    return render(request, 'customer/order.html', {
        'order': product_variant,
        'addresses': addresses,
        'default_address': default_address
    })

    #----------Cart-Checkout|Cart-Order-------------
@login_required
def checkout(request, cart_id):
    user = request.user
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    addresses = Address.objects.filter(user=user).order_by('-is_default', '-updated_at')

    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()

    subtotal = sum(item.price_at_time * item.quantity for item in cart_items)
    tax = round(subtotal * Decimal('0.08'), 2)
    grand_total = subtotal + tax

    return render(request, 'customer/order.html', {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'is_cart_checkout': True
    })


@login_required
def order_select_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    
    product_slug = request.GET.get('product_slug')
    if product_slug:
        return redirect('order', slug=product_slug)
    return redirect('customer_dashboard')

#---------------Placed Order----------------------------------
@login_required
def place_order(request):
    if request.method =="POST":
        user=request.user

        payment_method = request.POST.get('payment_method')
        variant_id=request.POST.get("variant_id")
        cart_id=request.POST.get("cart_id")
    
        address=Address.objects.filter(user=user, is_default=True).first()

        if not address:
            messages.error(request,"Please Add a Delivery Address.")
            return redirect("customer_address_add")

        order_number="SpyO-" + uuid.uuid4().hex[:10].upper()

    #-----------Cart checkout-----------------------------
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id, user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                messages.error(request,"Your cart is empty.")
                return redirect("view_cart")

            total_amount = sum(item.price_at_time * item.quantity for item in cart_items)

            #----Create order-----
            order=Order.objects.create(
                user=user,
                order_number=order_number,
                total_amount=total_amount,
                payment_method=payment_method,
                address=address
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    seller=item.variant.product.seller,
                    quantity=item.quantity,
                    price_at_purchase=item.price_at_time
                )
            #----Cart_delete----
            cart_items.delete()
            cart.total_amount = 0
            cart.save()

            # messages.success(request,f"ORDER Placed Successfully! Order Number: {order_number}")
            # return redirect("order_confirmation", order_id=order.id)

    #-------Single Product Checkout--------------
        else:
            if not variant_id:
                messages.error(request,"Invalid order request.")
                return redirect("customer_home")

            variant=get_object_or_404(ProductVariant, id=variant_id)

            order=Order.objects.create(
                user=user,
                order_number=order_number,
                total_amount=variant.selling_price,
                payment_method=payment_method,
                address=address
            )
            OrderItem.objects.create(
                order=order,
                variant=variant,
                seller=variant.product.seller,
                quantity=1,
                price_at_purchase=variant.selling_price
            )
            # messages.success(request,f"ORDER Placed SuccessFully! Order Number: {order_number}")
            # return redirect("order_confirmation", order_id=order.id)
        
        #----Payment(COD|ONLINE)----

        if payment_method == "COD":
            order.payment_status = "PENDING"
            order.save()

            messages.success(request, f"Order Placed! Order Number: {order_number}")
            return redirect("order_confirmation", order_id=order.id)
        
        elif payment_method == "ONLINE":
            order.payment_status = "PENDING"
            order.save()

            return redirect("create_payment", order_id=order.id)

    return redirect("customer_home")


#--------Order_confirmation/Order_history/Reorder---------------------
@login_required
def order_confirmation(request,order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_item=OrderItem.objects.filter(order=order)
    return render(request,"customer/order_confirmation.html",{"order":order,"order_item":order_item})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-ordered_at')

    filter_type = request.GET.get("filter")
    if filter_type == "3months":
        three_month_ago = timezone.now() - timedelta(days=90)
        orders = orders.filter(ordered_at__gte=three_month_ago)

    return render(request,"customer/order_history.html",{"orders":orders})

@login_required
def reorder(request,order_id):
    order=get_object_or_404(Order,id=order_id,user=request.user)
    cart,created=Cart.objects.get_or_create(user=request.user)

    for item in order.items.all():
        CartItem.objects.create(
            cart=cart,
            variant=item.variant,
            quantity=item.quantity,
            price_at_time=item.variant.selling_price
        )
    messages.success(request,"Items added to Cart Again.")
    return redirect("view_cart")

#----------------Search---------------------
# def search(request):
#     search=request.GET.get("search")
#     if search:
#         products=Product.objects.filter(
#             Q(name__icontains=search) |
#             Q(brand__icontains=search) |
#             Q(subcategory__name__icontains=search) |
#             Q(subcategory__category__name__icontains=search),
#             is_active=True).distinct()
#     return render(request,"customer/search.html",{"products":products,"search":search})

def search(request):
    search=request.GET.get("search")

    brand=request.GET.getlist('brand')
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort")

    products = Product.objects.filter(is_active=True)
    if search:
        words=search.split()
        q_object=Q()

        for searchs in words:
            q_object |= Q(name__icontains=searchs)
            q_object |= Q(brand__icontains=searchs)
            q_object |= Q(subcategory__name__icontains=searchs)
            q_object |= Q(subcategory__category__name__icontains=searchs)
            q_object |= Q(model_number__icontains=searchs)
        products=Product.objects.filter(q_object).distinct()

        if brand:
            products=products.filter(brand__in=brand)

        if min_price and min_price.isdigit():
            products=products.filter(variants__selling_price__gte=int(min_price))

        if max_price and max_price.isdigit():
            products=products.filter(variants__selling_price__lte=int(max_price))

        if sort == "low":
            products = products.order_by("variants__selling_price")

        elif sort == "high":
            products = products.order_by("-variants__selling_price")

        elif sort == "new":
            products = products.order_by("-created_at")

        all_brands = Product.objects.values_list("brand", flat=True).distinct()

    return render(request,"customer/search.html",{"products":products,"search":search,'all_brands': all_brands,
                                                  'min_price': min_price,'max_price': max_price,"sort":sort})

def live_search(request):
    search=request.GET.get("search")
    results = []
    if search:
        products=Product.objects.filter(Q(name__icontains=search) | Q(brand__icontains=search),is_active=True)[:5]
        results=list(products.values("name","slug"))
    return JsonResponse(results, safe=False)

#---------------------Review--------------------------------


def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review", "")
        
        Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            comment=review
        )
        messages.success(request, "Thank you for your review!")
        return redirect('single_product_variant', slug=product.slug)
    
    return render(request, "customer/add_Review.html", {"product": product})


#---------------------Payment|Razorpay--------------------------------
def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

    amount = int(order.total_amount * 100)

    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment, created = Payment.objects.get_or_create(order=order)

    payment.razorpay_order_id = razorpay_order['id']
    payment.amount = amount
    payment.payment_status = "PENDING"
    payment.save()

    order.payment_method = "ONLINE"
    order.payment_status = "PENDING"
    order.save()

    return render(request, "customer/payment.html", {"order": order,"payment": payment,"items": order.items.all(),"amount_rupees": payment.amount / 100,"key": settings.RAZORPAY_KEY})


def payment_success(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        payment = Payment.objects.get(razorpay_order_id=order_id)

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.payment_status = "SUCCESS"
        payment.save()

        order = payment.order
        order.payment_status = "SUCCESS"
        order.save()

        return redirect('order_confirmation', order_id=order.id)

    except:
        payment = Payment.objects.get(razorpay_order_id=order_id)
        payment.payment_status = "FAILED"
        payment.save()

        return HttpResponse("Payment Failed")