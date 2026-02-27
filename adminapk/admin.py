from django.contrib import admin
from .models import (
    Offer,
    Discount,
    Coupon,
    OfferDiscountBridge,
    ProductOfferBridge,
    CategoryOfferBridge,
    ProductDiscountBridge,
    CategoryDiscountBridge,
    PlatformCommission,
)

admin.site.register(Offer)
admin.site.register(Discount)
admin.site.register(Coupon)
admin.site.register(OfferDiscountBridge)
admin.site.register(ProductOfferBridge)
admin.site.register(CategoryOfferBridge)
admin.site.register(ProductDiscountBridge)
admin.site.register(CategoryDiscountBridge)
admin.site.register(PlatformCommission)