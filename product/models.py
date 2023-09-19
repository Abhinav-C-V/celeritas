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
    product_discount = models.IntegerField(null=True, blank=True)  # Added product-specific discount
    offer_active = models.BooleanField(default=False)
    
    def get_best_discount(self):
        # Get the discount for the associated category, default to 0 if no discount
        category_discount = self.category.discount or 0
        
        # Get the product-specific discount, default to 0 if no discount
        product_discount = self.product_discount or 0
        
        # Calculate the best discount for the product (either category discount or product-specific discount)
        return max(category_discount, product_discount, 0)

    @property
    def price(self):
        # Calculate the price after applying the best discount
        best_discount = self.get_best_discount()
        if int(self.normal_price) > best_discount:
            return int(self.normal_price) - best_discount
        return int(self.normal_price)

    def get_url(self):
        return reverse('product_detail', args=[self.id,])

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


