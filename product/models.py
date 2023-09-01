from django.db import models
from category.models import Category
# from home_store.models import UserDetail
from django.urls import reverse
from django.db.models import Sum
# from . models import Variation
# Create your models here.



class Product(models.Model):
    product_name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    normal_price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_gallery/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # created_date = models.DateTimeField(auto_now_add=True)
    
    @property
    def price(self):
        if self.category.discount is None:
            return int(self.normal_price)
        else:  
            return int(self.normal_price) - int(self.category.discount)
  
    def get_url(self):
        return reverse('product_detail', args = [self.id,])

    def __str__(self):
        return self.product_name

    
    

# class ProductGallery(models.Model):
#     product = models.ForeignKey(Variation, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='product_gallery/')

#     def __str__(self):
#         return f"Gallery Image for {self.product.product_name}"


class Color(models.Model):
    color = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.color.upper()
    
    
class Size(models.Model):
    size = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.size.upper()


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, default=None)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, max_length=50, null=True, blank=True)
    stock = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"product: {self.product}, Colour: {self.color}, Size: {self.size}"

class ProductGallery(models.Model):
    product = models.ForeignKey(Variation, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return f"Gallery Image for {self.product.product.product_name}"


