from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from product.models import Variation

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

    def __str__(self):
        return f"{self.user_firstname} {self.user_lastname}"

    def set_password(self, raw_password):
        self.user_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.user_password)
    


class Banner(models.Model):
    name = models.CharField(max_length=50,default=None)
    image = models.ImageField(upload_to='image_space/banner',default=None)
    
    def __str__(self):
        return self.name
    

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
    
# STATUS_CHOICES = (
#     ('Pending', 'Pending'),
#     ('Accepted', 'Accepted'),
#     ('Packed', 'Packed'),
#     ('On the way', 'On the way'),
#     ('Delivered', 'Delivered'),
#     ('Cancel Requested', 'Cancel Requested'),
#     ('Return Requested', 'Return Requested'),
#     ('Cancelled', 'Cancelled'),
#     ('Returned', 'Returned'),
# )
# TYPE_CHOICES = (
#     ('Cash on delivery', 'Cash on delivery'),
#     ('Paypal', 'Paypal'),
#     ('Razorpay', 'Razorpay'),
# )
# class Order(models.Model):
#     user = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
#     address = models.ForeignKey(Address, on_delete=models.CASCADE)
#     product = models.ForeignKey(Variation, on_delete=models.CASCADE)
#     amount = models.IntegerField(default=0)
#     ordered_date = models.DateTimeField(auto_now_add=True)
#     ordertype = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Cash on delivery')
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
#     def __str__(self):
#         return str(self.id)
