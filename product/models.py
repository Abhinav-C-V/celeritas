from django.db import models
from category.models import Category
from django.urls import reverse
from django.db.models import Sum
from home_store.models import UserDetail
from django.db.models import Avg, Count
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
    
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True ).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True ).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    

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
    
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.subject


