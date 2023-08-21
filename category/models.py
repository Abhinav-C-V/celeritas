from django.db import models

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    offer_active = models.BooleanField(default=False)
    discount = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'