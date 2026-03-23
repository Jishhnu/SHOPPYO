import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Page.settings')

import django
django.setup()

from faker import Faker
import random
from django.utils.text import slugify
from django.utils import timezone

from core.models import Category, SubCategory
from seller.models import Product, ProductVariant, ProductImage, SellerProfile
from seller.models import AttributeOption, VariantAttributeBridge

fake = Faker()

def add_20_products():
    print("Adding 20 realistic products...")
    
    # Get existing dependencies (assume dummy.py run)
    sellers = list(SellerProfile.objects.all())
    subcategories = list(SubCategory.objects.all())
    
    if not sellers:
        print("No sellers found! Run dummy.py first.")
        return
    if not subcategories:
        print("No subcategories found! Run dummy.py first.")
        return
    
    # Realistic product data: list of dicts for variety
    product_data = [
        {'name': 'iPhone 15 Pro Max', 'brand': 'Apple', 'desc': 'Latest iPhone with A17 Pro chip, Titanium design, 48MP camera.', 'subcat_slug': 'smartphones'},
        {'name': 'Samsung Galaxy S24 Ultra', 'brand': 'Samsung', 'desc': 'Flagship Android with S Pen, 200MP camera, AI features.', 'subcat_slug': 'smartphones'},
        {'name': 'MacBook Pro 14 M3', 'brand': 'Apple', 'desc': 'M3 chip, Liquid Retina XDR display, up to 22hr battery.', 'subcat_slug': 'laptops'},
        {'name': 'Dell XPS 13', 'brand': 'Dell', 'desc': 'Ultra-slim laptop with Intel Core Ultra, InfinityEdge display.', 'subcat_slug': 'laptops'},
        {'name': 'Sony WH-1000XM5', 'brand': 'Sony', 'desc': 'Best noise-cancelling headphones with 30hr battery, LDAC.', 'subcat_slug': 'headphones'},
        {'name': 'AirPods Pro 2', 'brand': 'Apple', 'desc': 'Active Noise Cancellation, Adaptive Transparency, USB-C.', 'subcat_slug': 'headphones'},
        {'name': 'Nikon Z6 III', 'brand': 'Nikon', 'desc': 'Mirrorless camera 24.5MP full-frame, 14fps burst.', 'subcat_slug': 'cameras'},
        {'name': 'Canon EOS R5', 'brand': 'Canon', 'desc': '8K video, 45MP sensor, Dual Pixel AF.', 'subcat_slug': 'cameras'},
        {'name': 'Nike Air Force 1', 'brand': 'Nike', 'desc': 'Classic low-top sneakers with leather upper, Air cushioning.', 'subcat_slug': 'sneakers'},
        {'name': 'Adidas Ultraboost', 'brand': 'Adidas', 'desc': 'Responsive Boost midsole, Primeknit upper.', 'subcat_slug': 'sneakers'},
        {'name': 'Levis 501 Original', 'brand': "Levi's", 'desc': 'Iconic straight fit jeans, 100% cotton.', 'subcat_slug': 'jeans'},
        {'name': 'Jack & Jones Slim Fit', 'brand': 'Jack & Jones', 'desc': 'Slim fit chinos for casual wear.', 'subcat_slug': 'jeans'},
        {'name': 'Dyson V15 Detect', 'brand': 'Dyson', 'desc': 'Cordless vacuum with laser dust detection.', 'subcat_slug': 'vacuums'},
        {'name': 'Philips Air Fryer', 'brand': 'Philips', 'desc': '6.2L capacity, Rapid Air tech, low oil.', 'subcat_slug': 'air-fryers'},
        {'name': 'IKEA Poang Chair', 'brand': 'IKEA', 'desc': 'Bentwood armchair with cushion.', 'subcat_slug': 'chairs'},
        {'name': 'Samsung 55" QLED TV', 'brand': 'Samsung', 'desc': '4K UHD, Quantum HDR, Gaming Hub.', 'subcat_slug': 'televisions'},
        {'name': 'LG 65" OLED', 'brand': 'LG', 'desc': 'Self-lit OLED, Dolby Vision, webOS.', 'subcat_slug': 'televisions'},
        {'name': "Harry Potter Box Set", 'brand': 'Bloomsbury', 'desc': 'Complete 7-book collection.', 'subcat_slug': 'fiction'},
        {'name': 'Sapiens by Yuval Noah', 'brand': 'Harvill Secker', 'desc': 'Brief history of humankind.', 'subcat_slug': 'non-fiction'},
        {'name': 'Kitchen Aid Stand Mixer', 'brand': 'KitchenAid', 'desc': '5.5Qt bowl, 10 speeds, planetary mixing.', 'subcat_slug': 'mixers'},
    ]
    
    products_added = 0
    for data in product_data:
        try:
            # Find subcat by slug-ish match or random
            subcat = next((s for s in subcategories if data['subcat_slug'] in s.slug.lower()), random.choice(subcategories))
            seller = random.choice(sellers)
            
            slug = slugify(data['name'])
            # Ensure unique slug
            while Product.objects.filter(slug=slug).exists():
                slug += f"-{random.randint(100,999)}"
            
            product = Product.objects.create(
                seller=seller,
                subcategory=subcat,
                name=data['name'],
                slug=slug,
                description=data['desc'],
                brand=data['brand'],
                model_number=f"{data['brand'][:3].upper()}-{random.randint(1000,9999)}",
                is_cancellable=True,
                is_returnable=True,
                return_days=30,
                approval_status='APPROVED',
                is_active=True
            )
            
            # Add 2-3 variants
            num_variants = random.randint(2, 3)
            for j in range(num_variants):
                mrp = round(random.uniform(1500, 8000), 2)
                discount = random.uniform(0.1, 0.4)
                selling_price = round(mrp * (1 - discount), 2)
                cost_price = round(selling_price * 0.7, 2)
                
                variant = ProductVariant.objects.create(
                    product=product,
                    sku_code=f"{slug.upper()[:8]}-V{j+1}",
                    mrp=mrp,
                    selling_price=selling_price,
                    cost_price=cost_price,
                    stock_quantity=random.randint(10, 100),
                    weight=round(random.uniform(0.1, 5.0), 2),
                    length=round(random.uniform(10, 100), 1),
                    width=round(random.uniform(5, 50), 1),
                    height=round(random.uniform(5, 50), 1),
                    tax_percentage=18.0
                )
                
                # Add 2-3 images
                for k in range(random.randint(2, 3)):
                    ProductImage.objects.create(
                        variant=variant,
                        image_url=f"https://picsum.photos/400/400?random={product.id*10 + j*3 + k}",
                        alt_text=f"{data['name']} image {k+1}",
                        is_primary=(k==0)
                    )
            
            products_added += 1
            print(f"Added: {data['name']}")
        except Exception as e:
            print(f"Error adding {data['name']}: {e}")
    
    print(f"Successfully added {products_added}/20 products.")

if __name__ == "__main__":
    add_20_products()

