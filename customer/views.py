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
    cart=Cart.objects.filter(user=request.user).first()
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
    wishlist=Wishlist.objects.get(user=request.user, wishlist_name="My Wishlist")
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


#-------------Product_variant---------------------------

@login_required
def single_product_variant(request,slug):
    product=get_object_or_404(Product, slug=slug)
    product_variant = ProductVariant.objects.get(product=product)
    product_image=ProductImage.objects.filter(variant=product_variant)
    return render(request,'customer/Single_variant.html',{'items':product_variant,'image':product_image})

#------------------Order---------------------------
@login_required
def order(request, id):
    product = get_object_or_404(Product, id=id)
    product_variant = ProductVariant.objects.get(product=product)
    
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
    
    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()
    
    return render(request, 'customer/order.html', {
        'order': product_variant,
        'addresses': addresses,
        'default_address': default_address
    })
@login_required
def checkout(request, cart_id):
    user = request.user
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    addresses = Address.objects.filter(user=user).order_by('-is_default', '-updated_at')

    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()

    # Calculate totals
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
    
    product_id = request.GET.get('product_id')
    if product_id:
        return redirect('order', id=product_id)
    return redirect('order')

#---------------Placed Order----------------------------------
@login_required
def place_order(request):
    user=request.user
    if request.method !="POST":
        return redirect("customer_home")
    
    variant_id=request.POST.get("variant_id")
    cart_id=request.POST.get("cart_id")
    payment_method=request.POST.get("payment_method")
    
    address=Address.objects.filter(user=user, is_default=True).first()

    if not address:
        messages.error(request,"Please Add a Delivery Address.")
        return redirect("customer_address_add")
    
    order_number="ORD-" + uuid.uuid4().hex[:10].upper()
    
    #-----------Cart checkout-----------------------------
    if cart_id:
        cart = get_object_or_404(Cart, id=cart_id, user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.error(request,"Your cart is empty.")
            return redirect("view_cart")
        
        total_amount = sum(item.price_at_time * item.quantity for item in cart_items)
        
        # Create order
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
        #cart_delete
        cart_items.delete()
        cart.total_amount = 0
        cart.save()
        
        messages.success(request,f"ORDER Placed Successfully! Order Number: {order_number}")
        return redirect("order_confirmation", order_id=order.id)
    
    #-------Single Product Checkout--------------
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
    messages.success(request,f"ORDER Placed SuccessFully! Order Number: {order_number}")
    return redirect("order_confirmation", order_id=order.id)

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