from django.contrib import admin
from .models import Product, ProductGallery, Variation, Color, Size

# Register your models here.

admin.site.register(Product)
admin.site.register(ProductGallery)
admin.site.register(Variation)
admin.site.register(Color)
admin.site.register(Size)

