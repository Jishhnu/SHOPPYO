from django.core import mail
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Address, Category, SubCategory
from customer.models import Order, OrderItem, Review
from seller.models import Product, ProductVariant, SellerProfile


User = get_user_model()


class SellerViewDecoratorTests(TestCase):
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
        cls.order = Order.objects.create(
            user=cls.customer,
            order_number="ORDER-001",
            total_amount=Decimal("1000.00"),
            payment_method="COD",
            address=cls.address,
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            variant=cls.variant,
            seller=cls.seller_profile,
            quantity=1,
            price_at_purchase=Decimal("1000.00"),
        )
        cls.review = Review.objects.create(
            user=cls.customer,
            product=cls.product,
            rating=5,
            comment="Great",
        )
        cls.pending_seller_user = User.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password="pass1234",
            role="SELLER",
        )
        cls.pending_seller_profile = SellerProfile.objects.create(
            user=cls.pending_seller_user,
            store_name="Pending Store",
            gst_number="GST999",
            pan_number="PAN999",
            bank_account_number="9999999999",
            ifsc_code="IFSC9999",
            business_address="Pending address",
            status="PENDING",
        )

    def _assert_redirects_to_login(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def _assert_role_access(self, name, kwargs=None, method="get", data=None, expected_status=200):
        kwargs = kwargs or {}
        url = reverse(name, kwargs=kwargs)

        client = self.client_class()
        request_method = getattr(client, method)
        anonymous_response = request_method(url, data=data or {})
        self._assert_redirects_to_login(anonymous_response)

        client.force_login(self.customer)
        wrong_role_response = request_method(url, data=data or {})
        self.assertEqual(wrong_role_response.status_code, 403)

        client.force_login(self.seller_user)
        allowed_response = request_method(url, data=data or {})
        self.assertEqual(allowed_response.status_code, expected_status)

    def test_non_mutating_seller_views_require_seller_role(self):
        protected_views = [
            ("seller_dashboard", {}, "get", None, 200),
            ("seller_profile", {}, "get", None, 200),
            ("seller_editprofile", {}, "get", None, 200),
            ("product_inventory", {}, "get", None, 200),
            ("seller_add_products", {}, "get", None, 200),
            ("get_subcategories", {}, "get", {"category_id": self.category.id}, 200),
            ("edit_product", {"id": self.product.id}, "get", None, 200),
            ("seller_order", {}, "get", None, 200),
            ("seller_order_details", {"order_id": self.order.id}, "get", None, 200),
            ("seller_review", {}, "get", None, 200),
            ("seller_reply_review", {"review_id": self.review.id}, "get", None, 200),
        ]

        for name, kwargs, method, data, expected_status in protected_views:
            with self.subTest(view=name):
                self._assert_role_access(name, kwargs, method, data, expected_status)

    def test_delete_product_requires_seller_role(self):
        product = Product.objects.create(
            seller=self.seller_profile,
            subcategory=self.subcategory,
            name="Delete Me",
            description="A phone",
            brand="BrandX",
            model_number="PX-DELETE",
            approval_status="APPROVED",
            is_active=True,
        )
        self._assert_role_access("delete_product", {"id": product.id}, expected_status=302)

    def test_seller_cancel_order_requires_seller_role(self):
        order = Order.objects.create(
            user=self.customer,
            order_number="ORDER-SELLER-CANCEL",
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
        self._assert_role_access("seller_cancel_order", {"order_id": order.id}, expected_status=302)

    def test_pending_seller_is_redirected_to_waiting_page_for_dashboard(self):
        self.client.force_login(self.pending_seller_user)
        response = self.client.get(reverse("seller_dashboard"))
        self.assertRedirects(response, reverse("seller_waiting"))

    def test_waiting_page_is_accessible_to_pending_seller(self):
        self.client.force_login(self.pending_seller_user)
        response = self.client.get(reverse("seller_waiting"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PENDING")

    def test_seller_logout_logs_out_seller(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse("seller_logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_seller_dashboard_contains_logout_link(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse("seller_dashboard"))
        self.assertContains(response, reverse("seller_logout"))
