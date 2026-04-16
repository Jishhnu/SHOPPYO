import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from core.models import Address, Category, SubCategory
from customer.models import Order
from seller.models import Product, ProductVariant, SellerProfile


User = get_user_model()


class AdminViewDecoratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="pass1234",
            role="CUSTOMER",
        )
        cls.admin_user = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="pass1234",
            role="ADMIN",
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
            status="PENDING",
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
            approval_status="PENDING",
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

        client.force_login(self.customer)
        if content_type:
            wrong_role_response = request_method(url, data=data or {}, content_type=content_type)
        else:
            wrong_role_response = request_method(url, data=data or {})
        self.assertEqual(wrong_role_response.status_code, 403)

        client.force_login(self.admin_user)
        if content_type:
            allowed_response = request_method(url, data=data or {}, content_type=content_type)
        else:
            allowed_response = request_method(url, data=data or {})
        self.assertEqual(allowed_response.status_code, expected_status)

    def test_non_mutating_admin_views_require_admin_role(self):
        protected_views = [
            ("admin_dashboard", {}, "get", None, 200, None),
            ("admin_logout", {}, "get", None, 302, None),
            ("admin_category", {}, "get", None, 200, None),
            (
                "toggle_category",
                {"id": self.category.id},
                "post",
                json.dumps({"is_active": False}),
                200,
                "application/json",
            ),
            ("admin_subcategory", {"slug": self.category.slug}, "get", None, 200, None),
            (
                "/admin_subcategory/toggle-subcategory/{}/".format(self.subcategory.id),
                {},
                "post",
                json.dumps({"is_active": False}),
                200,
                "application/json",
            ),
            ("admin_sellerverification", {}, "get", None, 200, None),
            ("admin_approvedsellers", {}, "get", None, 200, None),
            ("admin_rejectsellers", {}, "get", None, 200, None),
            ("admin_suspendedsellers", {}, "get", None, 200, None),
            ("admin_productverification", {}, "get", None, 200, None),
            ("admin_approvedproduct", {}, "get", None, 200, None),
            ("admin_rejectproduct", {}, "get", None, 200, None),
            ("admin_users", {}, "get", None, 200, None),
            ("admin_orders", {}, "get", None, 200, None),
            ("admin_order_detail", {"id": self.order.id}, "get", None, 200, None),
        ]

        for name, kwargs, method, data, expected_status, content_type in protected_views:
            with self.subTest(view=name):
                if name.startswith("/"):
                    client = self.client_class()
                    request_method = getattr(client, method)
                    anonymous_response = request_method(name, data=data or {}, content_type=content_type)
                    self._assert_redirects_to_login(anonymous_response)

                    client.force_login(self.customer)
                    wrong_role_response = request_method(name, data=data or {}, content_type=content_type)
                    self.assertEqual(wrong_role_response.status_code, 403)

                    client.force_login(self.admin_user)
                    allowed_response = request_method(name, data=data or {}, content_type=content_type)
                    self.assertEqual(allowed_response.status_code, expected_status)
                else:
                    self._assert_role_access(name, kwargs, method, data, expected_status, content_type)

    def test_delete_admin_category_requires_admin_role(self):
        category = Category.objects.create(name="Delete Category", slug="delete-category")
        self._assert_role_access("delete_admin_category", {"slug": category.slug}, expected_status=302)

    def test_delete_admin_subcategory_requires_admin_role(self):
        category = Category.objects.create(name="Delete Parent", slug="delete-parent")
        subcategory = SubCategory.objects.create(
            category=category,
            name="Delete Child",
            slug="delete-child",
        )
        self._assert_role_access("delete_admin_subcategory", {"slug": subcategory.slug}, expected_status=302)

    def test_user_toggle_requires_admin_role(self):
        customer = User.objects.create_user(
            username="toggle@example.com",
            email="toggle@example.com",
            password="pass1234",
            role="CUSTOMER",
            is_active=True,
        )
        self._assert_role_access("user_toggle", {"id": customer.id, "action": "deactivate"}, expected_status=302)

    def test_approval_email_is_sent_when_admin_approves_seller(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("admin_sellerverification"),
            {"seller_id": self.seller_profile.id, "action": "approve"},
        )

        self.assertRedirects(response, reverse("admin_sellerverification"))
        self.seller_profile.refresh_from_db()
        self.assertEqual(self.seller_profile.status, "APPROVED")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("approved", mail.outbox[0].subject.lower())
        self.assertEqual(mail.outbox[0].to, [self.seller_user.email])

    def test_rejection_email_is_sent_when_admin_rejects_seller(self):
        self.seller_profile.status = "APPROVED"
        self.seller_profile.save()
        mail.outbox = []

        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("admin_approvedsellers"),
            {"seller_id": self.seller_profile.id, "action": "reject"},
        )

        self.assertRedirects(response, reverse("admin_approvedsellers"))
        self.seller_profile.refresh_from_db()
        self.assertEqual(self.seller_profile.status, "REJECTED")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("status update", mail.outbox[0].subject.lower())
        self.assertEqual(mail.outbox[0].to, [self.seller_user.email])
