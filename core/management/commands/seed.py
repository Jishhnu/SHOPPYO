from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils import timezone

from core.models import User, Address, Category, SubCategory, Notification
from seller.models import (
    SellerProfile, Product, ProductVariant,
    ProductImage, Attribute, AttributeOption,
    VariantAttributeBridge, InventoryLog
)
from customer.models import (
    Cart, CartItem, Wishlist, WishlistItem,
    Review, Order, OrderItem
)
from adminapk.models import (
    Offer, Discount, Coupon,
    OfferDiscountBridge, ProductOfferBridge, CategoryOfferBridge,
    ProductDiscountBridge, CategoryDiscountBridge,
    PlatformCommission
)

fake = Faker()


class Command(BaseCommand):
    help = "FULL DATABASE SEEDER 🚀"

    def handle(self, *args, **kwargs):

        # ---------------- CLEAN DB ----------------
        self.stdout.write("Clearing old data...")
        PlatformCommission.objects.all().delete()
        Coupon.objects.all().delete()
        CategoryDiscountBridge.objects.all().delete()
        ProductDiscountBridge.objects.all().delete()
        CategoryOfferBridge.objects.all().delete()
        ProductOfferBridge.objects.all().delete()
        OfferDiscountBridge.objects.all().delete()
        Offer.objects.all().delete()
        Discount.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        WishlistItem.objects.all().delete()
        Wishlist.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        InventoryLog.objects.all().delete()
        VariantAttributeBridge.objects.all().delete()
        AttributeOption.objects.all().delete()
        Attribute.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        SellerProfile.objects.all().delete()
        SubCategory.objects.all().delete()
        Category.objects.all().delete()
        Notification.objects.all().delete()
        Address.objects.all().delete()
        User.objects.all().delete()

        # ---------------- USERS ----------------
        users = []
        for i in range(20):
            user = User.objects.create(
                username=f"user{i}",
                email=f"user{i}@mail.com",
                phone_number=f"99999{i:05}",
                role=random.choice(['CUSTOMER', 'SELLER']),
                is_verified=True
            )
            user.set_password("password123")
            user.save()
            users.append(user)

        # ---------------- ADDRESS ----------------
        for user in users:
            Address.objects.create(
                user=user,
                full_name=fake.name(),
                phone_number=user.phone_number,
                pincode="682001",
                locality=fake.street_name(),
                house_info=fake.building_number(),
                city="Kochi",
                state="Kerala",
                address_type=random.choice(['HOME', 'WORK']),
                is_default=True
            )

        # ---------------- CATEGORY ----------------
        categories = []
        for i in range(10):
            cat = Category.objects.create(
                name=f"Category {i}",
                slug=f"category-{i}",
                image_url="https://picsum.photos/300"
            )
            categories.append(cat)

        # ---------------- SUBCATEGORY ----------------
        subcategories = []
        for i in range(20):
            sub = SubCategory.objects.create(
                category=random.choice(categories),
                name=f"SubCategory {i}",
                slug=f"subcat-{i}",
                image_url="https://picsum.photos/200"
            )
            subcategories.append(sub)

        # ---------------- SELLERS ----------------
        sellers = []
        for i, user in enumerate(users[:8]):
            seller = SellerProfile.objects.create(
                user=user,
                store_name=fake.company(),
                store_slug=fake.slug() + str(i),
                gst_number=fake.bothify(text='GST#####'),
                pan_number=fake.bothify(text='PAN#####'),
                bank_account_number=fake.bban(),
                ifsc_code=fake.bothify(text='IFSC####'),
                business_address=fake.address(),
                is_verified=True
            )
            sellers.append(seller)

        # ---------------- ATTRIBUTES ----------------
        color_attr = Attribute.objects.create(name="Color")
        size_attr = Attribute.objects.create(name="Size")

        colors = ["Red", "Blue", "Black", "White"]
        sizes = ["S", "M", "L", "XL"]

        color_opts = [AttributeOption.objects.create(attribute=color_attr, value=c) for c in colors]
        size_opts = [AttributeOption.objects.create(attribute=size_attr, value=s) for s in sizes]

        # ---------------- PRODUCTS ----------------
        products = []
        for i in range(50):
            product = Product.objects.create(
                seller=random.choice(sellers),
                subcategory=random.choice(subcategories),
                name=fake.word(),
                slug=f"product-{i}",
                description=fake.text(),
                brand=fake.company(),
                model_number=f"MDL{i}",
                approval_status="APPROVED"
            )
            products.append(product)

            for j in range(random.randint(1, 3)):
                mrp = random.randint(500, 5000)
                selling = mrp - random.randint(50, 500)

                variant = ProductVariant.objects.create(
                    product=product,
                    sku_code=f"SKU-{i}-{j}",
                    mrp=mrp,
                    selling_price=selling,
                    cost_price=selling - 50,
                    stock_quantity=random.randint(5, 50),
                    tax_percentage=18
                )

                ProductImage.objects.create(
                    variant=variant,
                    image_url="https://picsum.photos/200",
                    is_primary=True
                )

                VariantAttributeBridge.objects.create(variant=variant, option=random.choice(color_opts))
                VariantAttributeBridge.objects.create(variant=variant, option=random.choice(size_opts))

                InventoryLog.objects.create(
                    variant=variant,
                    change_amount=variant.stock_quantity,
                    reason="Initial",
                    performed_by=random.choice(users)
                )

        # ---------------- CART ----------------
        for user in users:
            cart = Cart.objects.create(user=user)
            variants = ProductVariant.objects.order_by('?')[:3]

            total = 0
            for v in variants:
                qty = random.randint(1, 2)
                CartItem.objects.create(cart=cart, variant=v, quantity=qty, price_at_time=v.selling_price)
                total += v.selling_price * qty

            cart.total_amount = total
            cart.save()

        # ---------------- WISHLIST ----------------
        for user in users:
            wishlist = Wishlist.objects.create(user=user)
            for v in ProductVariant.objects.order_by('?')[:5]:
                WishlistItem.objects.create(wishlist=wishlist, variant=v)

        # ---------------- REVIEWS ----------------
        for _ in range(100):
            Review.objects.create(
                user=random.choice(users),
                product=random.choice(products),
                rating=random.randint(1, 5),
                comment=fake.sentence()
            )

        # ---------------- ORDERS ----------------
        for user in users:
            address = user.addresses.first()
            if not address:
                continue

            variants = ProductVariant.objects.order_by('?')[:3]
            total = 0

            order = Order.objects.create(
                user=user,
                order_number=f"ORD{random.randint(10000,99999)}",
                total_amount=0,
                payment_method=random.choice(['COD', 'ONLINE']),
                payment_status=random.choice(['PENDING', 'PAID']),
                order_status=random.choice(['PLACED', 'DELIVERED']),
                address=address
            )

            for v in variants:
                qty = random.randint(1, 2)
                OrderItem.objects.create(
                    order=order,
                    variant=v,
                    seller=v.product.seller,
                    quantity=qty,
                    price_at_purchase=v.selling_price
                )
                total += v.selling_price * qty

            order.total_amount = total
            order.save()

        # ---------------- OFFERS / DISCOUNTS ----------------
        discounts = [Discount.objects.create(
            name=f"Discount {i}",
            discount_type=random.choice(['PERCENTAGE', 'FLAT']),
            discount_value=random.randint(10, 50)
        ) for i in range(5)]

        offers = [Offer.objects.create(
            title=f"Offer {i}",
            description=fake.text(),
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        ) for i in range(5)]

        for offer in offers:
            OfferDiscountBridge.objects.create(offer=offer, discount=random.choice(discounts))

        for product in products[:20]:
            ProductOfferBridge.objects.create(product=product, offer=random.choice(offers))

        for cat in categories:
            CategoryOfferBridge.objects.create(category=cat, offer=random.choice(offers))

        for product in products[20:40]:
            ProductDiscountBridge.objects.create(product=product, discount=random.choice(discounts))

        for cat in categories:
            CategoryDiscountBridge.objects.create(category=cat, discount=random.choice(discounts))

        # ---------------- COUPONS ----------------
        for i in range(5):
            Coupon.objects.create(
                code=f"CODE{i}",
                discount_value=random.randint(50, 200),
                valid_from=timezone.now(),
                valid_to=timezone.now() + timezone.timedelta(days=15),
                usage_limit=100
            )

        # ---------------- COMMISSION ----------------
        for item in OrderItem.objects.all():
            percent = random.randint(5, 15)
            PlatformCommission.objects.create(
                seller=item.seller,
                order_item=item,
                commission_percentage=percent,
                commission_amount=(item.price_at_purchase * item.quantity) * percent / 100
            )

        # ---------------- NOTIFICATIONS ----------------
        for user in users:
            Notification.objects.create(
                user=user,
                title="Offer!",
                message=fake.sentence()
            )

        self.stdout.write(self.style.SUCCESS("DATABASE FULLY SEEDED"))