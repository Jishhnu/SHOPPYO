from django.db import models
from core.models import User, SubCategory
from django.utils.text import slugify

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=255)
    store_slug = models.SlugField(unique=True)
    gst_number = models.CharField(max_length=50)
    pan_number = models.CharField(max_length=50)
    bank_account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    business_address = models.TextField()
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES =[
        ('PENDING', 'Pending'),
        ('APPROVED','Approved'),
        ('REJECTED','Rejected'),
    ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='PENDING')
    suspended_until = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.store_slug:
            self.store_slug = slugify(self.store_name)
        super().save(*args, **kwargs)

class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    is_cancellable = models.BooleanField(default=True)
    is_returnable = models.BooleanField(default=True)
    return_days = models.IntegerField(default=7)

    approval_status = models.CharField(max_length=20, choices=(
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')),default='PENDING')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku_code = models.CharField(max_length=100, unique=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    weight = models.FloatField(help_text="Weight in kg",null=True,blank=True)
    length = models.FloatField(help_text="Length in cm",null=True,blank=True)
    width = models.FloatField(help_text="Width in cm",null=True,blank=True)
    height = models.FloatField(help_text="Height in cm",null=True,blank=True)
    tax_percentage = models.FloatField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discount_percentage(self):
        if self.mrp > self.selling_price:
            discount = ((self.mrp - self.selling_price) / self.mrp) * 100
            return int(discount)
        return 0
    
    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="images")
    # image_url = models.URLField()
    image = models.ImageField(upload_to='products/',null=True,blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)


class Attribute(models.Model):
    name = models.CharField(max_length=100) # e.g., Color, Size

class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=100) # e.g., Red, XL

class VariantAttributeBridge(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    option = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)

class InventoryLog(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)