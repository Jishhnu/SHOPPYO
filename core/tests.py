from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from seller.models import SellerProfile


User = get_user_model()

#---This test class verifies role-based redirection based on their role and status----

class CoreRoleRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(
            username="customer@example.com",
            email="customer@example.com",
            password="pass1234",
            role="CUSTOMER",
        )
        cls.seller = User.objects.create_user(
            username="seller@example.com",
            email="seller@example.com",
            password="pass1234",
            role="SELLER",
        )
        cls.seller_profile = SellerProfile.objects.create(
            user=cls.seller,
            store_name="Seller Store",
            gst_number="GST123",
            pan_number="PAN123",
            bank_account_number="1234567890",
            ifsc_code="IFSC0001",
            business_address="Seller address",
            status="APPROVED",
        )
        cls.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="pass1234",
            role="ADMIN",
        )
        cls.pending_seller = User.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password="pass1234",
            role="SELLER",
        )
        cls.pending_seller_profile = SellerProfile.objects.create(
            user=cls.pending_seller,
            store_name="Pending Store",
            gst_number="GST999",
            pan_number="PAN999",
            bank_account_number="9999999999",
            ifsc_code="IFSC9999",
            business_address="Pending address",
            status="PENDING",
        )

    def test_authenticated_seller_is_redirected_from_customer_home(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse("customer_home"))
        self.assertRedirects(response, reverse("seller_dashboard"))

    def test_authenticated_admin_is_redirected_from_customer_home(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("customer_home"))
        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_authenticated_customer_stays_on_customer_home(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("customer_home"))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_seller_is_redirected_away_from_login(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("seller_dashboard"))

    def test_pending_seller_is_redirected_to_waiting_from_login(self):
        self.client.force_login(self.pending_seller)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("seller_waiting"))
