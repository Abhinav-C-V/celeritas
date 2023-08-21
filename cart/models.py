from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from home_store.models import UserDetail, Address
from product.models import Product, Variation
# Create your models here.


class Wishlist(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE,default=None)
    product = models.ForeignKey(Product,  on_delete=models.CASCADE,default=None)
    
    def __str__(self):
        return f"{self.user.user_email} , {self.product.product_name}"


     
class Cart(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False, related_name='items')
    product = models.ForeignKey(Variation, on_delete=models.CASCADE, null=False)
    quantity = models.PositiveIntegerField()
    

    @property
    def subtotal(self):
        return self.product.product.price * self.quantity
    

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=30)
    is_active=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=0)
    minimum_amount=models.IntegerField(default=500)
    description = models.CharField(max_length=200,null=True,default='Sample')
    def __str__(self):
        return self.coupon_code

class UserCoupon(models.Model):
    coupon=models.ForeignKey(Coupon, on_delete=models.CASCADE, null=False)
    user=models.ForeignKey(UserDetail, on_delete=models.CASCADE, null=False)
    applied=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.user_firstname} , {self.coupon.coupon_code} , {self.applied}"


STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancel Requested', 'Cancel Requested'),
    ('Return Requested', 'Return Requested'),
    ('Cancelled', 'Cancelled'),
    ('Returned', 'Returned'),
)
TYPE_CHOICES = (
    ('Cash on delivery', 'Cash on delivery'),
    ('Paypal', 'Paypal'),
    ('Razorpay', 'Razorpay'),
)
class Order(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    product = models.ForeignKey(Variation, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    quantity = models.IntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    order_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Cash on delivery')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return str(self.id)