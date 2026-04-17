from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Address, Category, SubCategory
from customer.models import Cart, CartItem, Order, OrderItem, Payment, Review, Wishlist, WishlistItem
from seller.models import Product, ProductVariant, SellerProfile


User = get_user_model()


class CustomerViewDecoratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="pass1234",
            role="CUSTOMER",
        )
        cls.seller_user = User.objects.create_user(
            username="seller@example.com",
            email="seller@example.com",
            password="pass1234",
            role="SELLER",
        )
        cls.admin_user = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="pass1234",
            role="ADMIN",
        )
        cls.seller_profile = SellerProfile.objects.create(
            user=cls.seller_user,
            store_name="Seller Store",
            gst_number="GST123",
            pan_number="PAN123",
            bank_account_number="1234567890",
            ifsc_code="IFSC0001",
            business_address="Seller address",
            status="APPROVED",
        )
        cls.category = Category.objects.create(name="Electronics", slug="electronics")
        cls.subcategory = SubCategory.objects.create(
            category=cls.category,
            name="Mobiles",
            slug="mobiles",
        )
        cls.product = Product.objects.create(
            seller=cls.seller_profile,
            subcategory=cls.subcategory,
            name="Phone",
            description="A phone",
            brand="BrandX",
            model_number="PX-1",
            approval_status="APPROVED",
            is_active=True,
        )
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku_code="SKU-001",
            mrp=Decimal("1200.00"),
            selling_price=Decimal("1000.00"),
            cost_price=Decimal("800.00"),
            stock_quantity=10,
            weight=1,
            length=1,
            width=1,
            height=1,
            tax_percentage=8,
        )
        cls.address = Address.objects.create(
            user=cls.customer,
            full_name="Customer User",
            phone_number="9999999999",
            pincode="123456",
            locality="Town",
            house_info="House",
            city="City",
            state="State",
            country="India",
            landmark="Near park",
            address_type="HOME",
            is_default=True,
        )
        cls.cart = Cart.objects.create(user=cls.customer, total_amount=Decimal("1000.00"))
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart,
            variant=cls.variant,
            quantity=1,
            price_at_time=Decimal("1000.00"),
        )
        cls.wishlist = Wishlist.objects.create(user=cls.customer, wishlist_name="My Wishlist")
        cls.wishlist_item = WishlistItem.objects.create(
            wishlist=cls.wishlist,
            variant=cls.variant,
        )
        cls.order = Order.objects.create(
            user=cls.customer,
            order_number="ORDER-001",
            total_amount=Decimal("1000.00"),
            payment_method="ONLINE",
            address=cls.address,
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            variant=cls.variant,
            seller=cls.seller_profile,
            quantity=1,
            price_at_purchase=Decimal("1000.00"),
        )
        cls.payment = Payment.objects.create(
            order=cls.order,
            razorpay_order_id="razor-order-1",
            amount=100000,
            payment_status="PENDING",
        )
        cls.review = Review.objects.create(
            user=cls.customer,
            product=cls.product,
            rating=5,
            comment="Great",
        )

    def _assert_redirects_to_login(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def _assert_role_access(self, name, kwargs=None, method="get", data=None, expected_status=200, content_type=None):
        kwargs = kwargs or {}
        url = reverse(name, kwargs=kwargs)

        client = self.client_class()
        request_method = getattr(client, method)
        if content_type:
            anonymous_response = request_method(url, data=data or {}, content_type=content_type)
        else:
            anonymous_response = request_method(url, data=data or {})
        self._assert_redirects_to_login(anonymous_response)

        client.force_login(self.seller_user)
        if content_type:
            wrong_role_response = request_method(url, data=data or {}, content_type=content_type)
        else:
            wrong_role_response = request_method(url, data=data or {})
        self.assertEqual(wrong_role_response.status_code, 403)

        client.force_login(self.customer)
        if content_type:
            allowed_response = request_method(url, data=data or {}, content_type=content_type)
        else:
            allowed_response = request_method(url, data=data or {})
        self.assertEqual(allowed_response.status_code, expected_status)

    def _create_cart_item(self):
        cart, _ = Cart.objects.get_or_create(user=self.customer, defaults={"total_amount": Decimal("0.00")})
        return CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1,
            price_at_time=Decimal("1000.00"),
        )

    def _create_wishlist_item(self):
        wishlist, _ = Wishlist.objects.get_or_create(user=self.customer, wishlist_name="My Wishlist")
        return WishlistItem.objects.create(
            wishlist=wishlist,
            variant=self.variant,
        )

    def _create_order(self, order_number):
        order = Order.objects.create(
            user=self.customer,
            order_number=order_number,
            total_amount=Decimal("1000.00"),
            payment_method="COD",
            address=self.address,
        )
        OrderItem.objects.create(
            order=order,
            variant=self.variant,
            seller=self.seller_profile,
            quantity=1,
            price_at_purchase=Decimal("1000.00"),
        )
        return order

    def test_non_mutating_customer_views_require_customer_role(self):
        protected_views = [
            ("customer_dashboard", {}, "get", None, 200, None),
            ("customer_update", {}, "get", None, 200, None),
            ("customer_logout", {}, "get", None, 302, None),
            ("customer_address", {}, "get", None, 200, None),
            ("customer_address_add", {}, "get", None, 200, None),
            ("customer_address_update", {"address_id": self.address.id}, "get", None, 200, None),
            ("customer_address_set_default", {"address_id": self.address.id}, "get", None, 302, None),
            ("view_cart", {}, "get", None, 200, None),
            ("wishlist_view", {}, "get", None, 200, None),
            ("order", {"slug": self.product.slug}, "get", None, 200, None),
            ("checkout", {"cart_id": self.cart.id}, "get", None, 200, None),
            ("order_select_address", {"address_id": self.address.id}, "get", None, 302, None),
            ("place_order", {}, "get", None, 302, None),
            ("order_confirmation", {"order_id": self.order.id}, "get", None, 200, None),
            ("order_history", {}, "get", None, 200, None),
            ("add_review", {"product_id": self.product.id}, "get", None, 200, None),
        ]

        for name, kwargs, method, data, expected_status, content_type in protected_views:
            with self.subTest(view=name):
                self._assert_role_access(name, kwargs, method, data, expected_status, content_type)

    def test_add_to_cart_requires_customer_role(self):
        self._assert_role_access("add_to_cart", {"variant_id": self.variant.id}, expected_status=302)

    def test_remove_from_cart_requires_customer_role(self):
        cart_item = self._create_cart_item()
        self._assert_role_access("remove_from_cart", {"item_id": cart_item.id}, expected_status=302)

    def test_cart_increase_requires_customer_role(self):
        cart_item = self._create_cart_item()
        self._assert_role_access("cart_increase", {"item_id": cart_item.id}, expected_status=302)

    def test_cart_decrease_requires_customer_role(self):
        cart_item = self._create_cart_item()
        self._assert_role_access("cart_decrease", {"item_id": cart_item.id}, expected_status=302)

    def test_add_to_wishlist_requires_customer_role(self):
        self._assert_role_access("add_to_wishlist", {"variant_id": self.variant.id}, expected_status=302)

    def test_remove_from_wishlist_requires_customer_role(self):
        wishlist_item = self._create_wishlist_item()
        self._assert_role_access("remove_wishlist", {"item_id": wishlist_item.id}, expected_status=302)

    def test_move_to_cart_requires_customer_role(self):
        wishlist_item = self._create_wishlist_item()
        self._assert_role_access("move_to_cart", {"item_id": wishlist_item.id}, expected_status=302)

    def test_move_all_to_cart_requires_customer_role(self):
        self._create_wishlist_item()
        self._assert_role_access("move_all_to_cart", expected_status=302)

    def test_reorder_requires_customer_role(self):
        order = self._create_order("ORDER-REORDER")
        self._assert_role_access("reorder", {"order_id": order.id}, expected_status=302)

    def test_cancel_order_requires_customer_role(self):
        order = self._create_order("ORDER-CANCEL")
        self._assert_role_access("cancel_order", {"order_id": order.id}, expected_status=302)

    def test_address_add_from_checkout_redirects_back_to_checkout(self):
        self.client.force_login(self.customer)
        checkout_url = reverse("checkout", kwargs={"cart_id": self.cart.id})
        response = self.client.post(
            reverse("customer_address_add"),
            {
                "full_name": "New Customer",
                "phone_number": "8888888888",
                "pincode": "654321",
                "locality": "New Town",
                "house_info": "Flat 1",
                "city": "New City",
                "state": "New State",
                "country": "India",
                "landmark": "Near school",
                "address_type": "HOME",
                "next": checkout_url,
            },
        )

        self.assertRedirects(response, checkout_url)

    @patch("customer.views.razorpay.Client")
    def test_create_payment_requires_customer_role(self, client_class):
        client_class.return_value.order.create.return_value = {"id": "razor-order-2"}
        self._assert_role_access(
            "create_payment",
            {"order_id": self.order.id},
            expected_status=200,
        )

    @patch("customer.views.razorpay.Client")
    def test_payment_success_requires_customer_role(self, client_class):
        client_class.return_value.utility.verify_payment_signature.return_value = None
        self._assert_role_access(
            "payment_success",
            method="get",
            data={
                "payment_id": "pay-1",
                "order_id": self.payment.razorpay_order_id,
                "signature": "sig-1",
            },
            expected_status=302,
        )
