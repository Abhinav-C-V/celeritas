from django.contrib.auth.hashers import make_password, check_password
from django.db import models
# from product.models import Variation, Product

# Create your models here.





class UserDetail(models.Model):
    user_firstname = models.CharField(max_length=50, default='')
    user_lastname  = models.CharField(max_length=50, default='')
    user_email     = models.CharField(max_length=50, unique= True)
    # user_name      = models.CharField(max_length=50, unique=True)
    user_phone     = models.CharField(max_length=50, null=True)
    user_password  = models.CharField(max_length=128) # Increase the length to accommodate the hashed password
    user_cpassword = models.CharField(max_length=128)
    user_is_active = models.BooleanField(default=True)
    user_image     = models.ImageField(upload_to='image_space/', null=True, blank=True)
    # is_admin       = models.BooleanField(default=False)
    
    USERNAME_FEILD = 'email'
    
    USER_CPASSWORD_FIELD = 'user_password'
    
    # def full_name(self):
    #     return f"{self.user_firstname} {self.user_lastname}"
    
    

    def __str__(self):
        return f"{self.user_firstname} {self.user_lastname}"

    def set_password(self, raw_password):
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)

    

STATE_CHOICES = (
    ('KARNATAKA', 'KARNATAKA'),
    ('KERALA', 'KERALA'),
    ('TAMIL NADU', 'TAMIL NADU'),
    ('GOA', 'GOA'),
    ('GUJARAT', 'GUJARAT')
)

class Address(models.Model):
    user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=12)
    housename = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50, default='KERALA')
    selected = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
# class ReviewRating(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
#     subject = models.CharField(max_length=100, blank=True)
#     review = models.TextField(max_length=500, blank=True)
#     rating = models.FloatField()
#     ip = models.CharField(max_length=20)
#     status = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     def __str__(self):
#         return self.subject

