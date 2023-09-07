from django import forms
from admn.models import Banner
from cart.models import Coupon, UserCoupon, Order
from product.models import Product, ProductGallery, Variation, Color, Size, ReviewRating
import re
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'normal_price', 'description', 'image', 'category']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'normal_price': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'product_name': 'Product Name',
            'normal_price': 'Normal Price',
            'description': 'Description',
            'category': 'Category',
        }
    
    def clean_normalprice(self):
        normal_price = self.cleaned_data['normalprice']
        if not re.match(r'^\d+(\.\d{1,2})?$', str(normal_price)):
            raise ValidationError("Price must be a number with up to 2 decimal places.")
        return normal_price




class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['product', 'color', 'size', 'stock']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product': 'Product',
            'size': 'Size',
            'colour': 'Color',
            'stock': 'Stock',
        }
    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise ValidationError("Stock must be a non-negative integer.")
        return stock


class ProductColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color']
        widgets = {
            'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'color': 'Colour',
        }
        
        
class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['size']
        widgets = {
            'size': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'size': 'Size',
        }



class ProductGalleryForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = ['product', 'image']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'product_name': 'Product Name',
            'image' : 'Image',
        }


        
class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['name', 'image']
        labels = {
            'name': 'Banner Name',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_code', 'is_active', 'discount_price', 'minimum_amount','description']
        labels = {
            'coupon_code': 'Coupon Code',
            'is_active': 'Is Active',
            'discount_price': 'Discount Price',
            'minimum_amount': 'Minimum Amount',
            'description': 'description',
        }
        widgets = {
            'coupon_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
class UserCouponForm(forms.ModelForm):
    class Meta:
        model = UserCoupon
        fields = ['coupon', 'user']
        labels = {
            'coupon': 'Coupon Code',
            'user': 'User',
        }
        widgets = {
            'coupon': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }
        
        
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type','status']
        widgets = {
            'order_type' : forms.Select(attrs={'class':'form-control'}),
            'status' : forms.Select(attrs={'class':'form-control'}),
        }
        labels={
            'order_type':'Order Type',
            'status':'Status',
        }
        

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'review': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'subject': 'subject',
            'review': 'review',
            'rating': 'rating',
        }