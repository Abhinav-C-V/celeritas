from django.db import models

# Create your models here.

class Banner(models.Model):
    name = models.CharField(max_length=50,default=None)
    image = models.ImageField(upload_to='image_space/banner',default=None)
    
    def __str__(self):
        return self.name
