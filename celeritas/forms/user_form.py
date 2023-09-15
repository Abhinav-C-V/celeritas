from django import forms
from home_store.models import UserDetail, Address
import re
from django.core.exceptions import ValidationError

class UserSignupForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['user_firstname', 'user_lastname', 'user_email', 'user_phone', 'user_image', 'user_password', 'user_cpassword']
        widgets = {
            'user_firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'user_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_phone': forms.NumberInput(attrs={'class': 'form-control'}),
            'user_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'user_cpassword': forms.PasswordInput(attrs={'class': 'form-control'}),
            'user_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'user_firstname': 'First Name',
            'user_lastname': 'Last Name',
            'user_email': 'Email',
            'user_phone': 'Phone no',
            'user_password': 'Password',
            'user_cpassword': 'Confirm Password',
            'user_image': 'Image',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('user_password')
        password_confirm = cleaned_data.get('user_cpassword')

        if password and password_confirm and password != password_confirm:
            self.add_error('user_cpassword', "Passwords do not match.")

        return cleaned_data

    def clean_user_phone(self):
        user_phone = self.cleaned_data['user_phone']
        if UserDetail.objects.filter(user_phone=user_phone).exists():
            raise forms.ValidationError("This Phone number already exists.")
        if not re.match(r'^\d{10}$', user_phone):
            raise forms.ValidationError("Phone number must be 10 digits.")
        return user_phone

    def clean_user_firstname(self):
        user_firstname = self.cleaned_data['user_firstname']
        if len(user_firstname) < 2:
            raise forms.ValidationError("First name must have at least 2 characters.")
        if not user_firstname.isalpha():
            raise forms.ValidationError("First name must only contain alphabetic characters.")
        return user_firstname

    def clean_user_lastname(self):
        user_lastname = self.cleaned_data['user_lastname']
        if len(user_lastname) < 1:
            raise forms.ValidationError("Last name must have at least 2 characters.")
        if not user_lastname.isalpha():
            raise forms.ValidationError("Last name must only contain alphabetic characters.")
        return user_lastname

    def clean_user_email(self):
        user_email = self.cleaned_data['user_email']
        if UserDetail.objects.filter(user_email=user_email).exists():
            raise forms.ValidationError("This email is already registered.")
        return user_email

    def clean_user_password(self):
        user_password = self.cleaned_data['user_password']
        if len(user_password) < 4 or len(user_password) > 10:
            raise forms.ValidationError("Password must be between 4 and 10 characters.")
        if not re.match(r'^[A-Za-z0-9]+$', user_password):
            raise forms.ValidationError("Password must only contain alphanumeric characters.")
        return user_password

    def clean_user_image(self):
        user_image = self.cleaned_data.get('user_image')
        if not user_image:
            raise forms.ValidationError('This field is required.')
        return user_image


   
class UserLoginForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['user_email','user_password']
        widgets = {
            'user_email' : forms.EmailInput(attrs={'class':'form-control'}),
            'user_password' : forms.PasswordInput(attrs={'class':'form-control'}),
        }
        labels={
            'user_email':'Email',
            'user_password':'Password',
        }
        
class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["name","housename", "locality", "phone", "city", "state", "zipcode"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'housename': forms.TextInput(attrs={'class': 'form-control'}),
            "locality": forms.TextInput(attrs={'class': 'form-control'}),
            "city": forms.TextInput(attrs={'class': 'form-control'}),
            "state": forms.Select(attrs={'class': 'form-control'}),
            "zipcode": forms.NumberInput(attrs={'class': 'form-control'}),
            "phone": forms.TextInput(attrs={'class': 'form-control'}),

        }
        labels={
            'name':'Name',
            'housename':'House Name',
            'locality':'Locality',
            'city':'City',
            'state':'State',
            'zipcode':'Zipcode',
            'phone':'Phone',
        }
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be entered in the format: '0000000000'")
        return phone

    def clean_zipcode(self):
        zipcode = self.cleaned_data['zipcode']
        if not re.match(r'^\d{6}$', str(zipcode)):
            raise ValidationError("Enter a valid zipcode.")
        return zipcode
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError("name must have at least 2 characters.")
        if not name.isalpha():
            raise forms.ValidationError("name must only contain alphabetic characters.")
        return name
    
