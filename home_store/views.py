from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, HttpResponse ,Http404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.views.generic import View
from celeritas.forms.user_form import UserSignupForm, UserLoginForm, UserAddressForm, WalletTransactionForm
from celeritas.forms.product_form import ReviewForm

from category.models import Category
from product.models import Product, ProductGallery, Variation, Size, Color, ReviewRating
from cart.models import Wishlist, Cart, CartItem, Coupon, UserCoupon, Wallet
from .models import UserDetail, Address
from admn.models import  Banner
# from cart.models import  Transaction

from django.db.models import Q, F
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.hashers import make_password, check_password
# from django.shortcuts import render, redirect
import os
from django.views import View
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage

from django.template.loader import render_to_string
# from django.core.mail import EmailMessage

# from django.core.mail import send_mail
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth import get_user_model
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text
# from django.urls import reverse

from cart.models import Order
from xhtml2pdf import pisa
from django.db.models import Q
import datetime
import math, random
from django.core.mail import send_mail
import string
# from django.urls import reverse
import os
from twilio.rest import Client
# from twilio.rest import Client



# Create your views here.


@never_cache
def index(request):
    if 'user_email' in request.session:
        return redirect('user_home')
    else:
        # print(make_password('1234'))
        cat=Category.objects.all()
        cat_id = request.GET.get('cat_id')
        prod = request.GET.get('prod_id')
        if cat_id is not None and prod is None:
            details3= Variation.objects.filter(product__category__id=cat_id).order_by('id')
        elif prod is not None and cat_id is None:
            details3= Variation.objects.filter(product__product_name__icontains=prod).order_by('id')
        elif prod is not None and cat_id is not None:
            details3= Variation.objects.filter(product__product_name__icontains=prod,product__category__id=cat_id).order_by('id')
        else:
            details3=Variation.objects.all().order_by('id')
        popular_pdt=details3.order_by('id')[:4]
        new_arivals=details3.order_by('-id')[:4]
        recommended = details3.order_by('product')[:4]
        
        obj = Banner.objects.all()
        context={ 
                # 'page_obj': page_obj,
                'cat':cat,
                'obj':obj,
                'new_arivals':new_arivals,
                'popular_pdt':popular_pdt,
                'recommended':recommended,
            }
        return render(request, 'index.html',context )

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')


class UserLoginView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'user_email' in request.session:
            return redirect('user_home')
        else:
            cat=Category.objects.all()
            form = UserLoginForm()
            return render(request, 'accounts/user_login.html', {'form': form, 'cat': cat})
    
    @method_decorator(never_cache)
    def post(self, request):
        user_email = request.POST.get('user_email')
        password = request.POST.get('user_password')
        user = UserDetail.objects.filter(user_email=user_email).first()
        if user and user.user_is_active is True and user.u_otp is None:
            # print(check_password(password, user.user_password))
            if check_password(password, user.user_password):  # Compare hashed passwords
            # if password == user.user_password:
                request.session['user_email'] = user_email
                return redirect('user_home')
            else:
                messages.warning(request, 'Incorrect password')
                return redirect('user_login')
        else:
            messages.warning(request, 'User Not Found')
            return redirect('user_login')



class UserSignupView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'user_email' in request.session:
            return redirect('home_store')
        form = UserSignupForm()
        cat=Category.objects.all()
        return render(request, 'accounts/user_register.html', {'form': form, 'cat': cat})
    
    @method_decorator(never_cache)
    def post(self, request):
        if 'user_email' in request.session:
            return redirect('home_store')
        cat=Category.objects.all()
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            password = request.POST.get('user_password')
            c_password = request.POST.get('user_cpassword')
            if c_password == password:
                u_otp = generateOTP()
                user = form.save(commit=False)
                user.user_password = make_password(password)  # Hash the password
                user.user_cpassword = make_password(c_password)  # Hash the password
                user.u_otp = u_otp
                
                htmlgen =  f'<p>Your OTP for sign up Celeritas account is <strong>{u_otp}</strong></p>.'
                otp_email = send_mail('OTP request',u_otp,'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
                
                if otp_email:
                    print('otp send to mail',u_otp)
                    user.save()
                    Wallet.objects.create(user=user)
                    request.session['u_otp'] = user.u_otp
                    return redirect('signup_otp')

                messages.warning(request, "Please enter a valid email address")
                return redirect('user_signup')
            else:
                messages.warning(request, "Passwords do not match")
                return redirect('user_signup')
        else:
            return render(request, 'accounts/user_register.html', {'form': form, 'cat': cat})
        

class SignupOTPView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'u_otp' in request.session:
            # Redirect the user to the registration page if registration data is not in the session
            cat = Category.objects.all()
            return render(request, 'accounts/signup_otp.html',{'cat':cat})
        else:
            return redirect('user_signup')
        
    @method_decorator(never_cache)
    def post(self, request):
        if 'u_otp' not in request.session:
            return redirect('user_signup')

        entered_otp = request.POST.get('u_otp')

        if entered_otp == request.session['u_otp']:
            try:
                user = UserDetail.objects.get(u_otp = entered_otp )
                user.u_otp = None
                user.save()
            except UserDetail.DoesNotExist:
                messages.warning(request,'please enter valid OTP')
                return redirect('signup_otp')
            del request.session['u_otp']
            if user:
                messages.success(request,'User successfully registered please login for explore Celeritas')
                return redirect('user_login')
        else:
            messages.warning(request, 'Invalid OTP. Please try again.')
            return redirect('signup_otp') 


@never_cache
def userlogout(request):
    if 'user_email' in request.session:
        del request.session['user_email']
        # print(request.session['user_email'])
    return redirect('user_index')


@never_cache
def userhome(request):
    if 'user_email' in request.session:
        cat=Category.objects.all()
        cat_id = request.GET.get('cat_id')
        prod = request.GET.get('prod_id')
        if cat_id is not None and prod is None:
            details3= Variation.objects.filter(product__category__id=cat_id).order_by('id')
        elif prod is not None and cat_id is None:
            details3= Variation.objects.filter(product__product_name__icontains=prod).order_by('id')
        elif prod is not None and cat_id is not None:
            details3= Variation.objects.filter(product__product_name__icontains=prod,product__category__id=cat_id).order_by('id')
        else:
            details3=Variation.objects.all().order_by('id')
        popular_pdt=details3.order_by('id')[:4]
        new_arivals=details3.order_by('-id')[:4]
        recommended = details3.order_by('product')[:4]

        obj = Banner.objects.all()
        # prod_count = Variation.objects.all().count()
        # brand_prod = prod_count/3
        # print(brand_prod)
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        
        context = {
            # 'page_obj': page_obj,
            'cat':cat,
            'obj':obj,
            'user_firstname': user_detail.user_firstname,
            'user_image': user_detail.user_image,
            'user':user_detail,
            'new_arivals':new_arivals,
            'popular_pdt':popular_pdt,
            'recommended':recommended,
        }
        return render(request, 'store/user_home.html', context)
    else:
         return redirect('user_login')
     
@never_cache
def userstore_filter(request):
    if 'user_email' in request.session:
        cat = Category.objects.all()
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        sizes = Size.objects.all()
        colors = Color.objects.all()
        details3 = Variation.objects.all()

        if request.method == 'POST':
            cat_name = request.POST.get('cat_id')
            size_id = request.POST.get('size_id')
            color_id = request.POST.get('color_id')
            min_prize = request.POST.get('min_prize')
            max_prize = request.POST.get('max_prize')
            
            if cat_name:
                details3 = details3.filter(product__category__id=cat_name)
            if size_id:
                details3 = details3.filter(size__id=size_id)
                
            if color_id:
                details3 = details3.filter(color__id=color_id)

            price_filter = Q()
            if min_prize:
                price_filter &= Q(product__normal_price__gt=min_prize)
                
            if max_prize:
                price_filter &= Q(product__normal_price__lte=max_prize)
                
            if price_filter:
                details3 = details3.filter(price_filter)

            details3 = details3.order_by('id')
        else:
            cat_name = request.GET.get('cat_id')
            size_id = request.GET.get('size_id')
            color_id = request.GET.get('color_id')
            min_prize = request.GET.get('min_prize')
            max_prize = request.GET.get('max_prize')
            
            
            if cat_name:
                details3 = details3.filter(product__category__id=cat_name)
            if size_id:
                details3 = details3.filter(size__id=size_id)
                
            if color_id:
                details3 = details3.filter(color__id=color_id)
                
            price_filter = Q()
            if min_prize:
                price_filter &= Q(product__normal_price__gt=min_prize)
                
            if max_prize:
                price_filter &= Q(product__normal_price__lte=max_prize)
                
            if price_filter:
                details3 = details3.filter(price_filter)

            details3 = details3.order_by('id')
            
        paginator = Paginator(details3, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'details3':details3,
            'page_obj': page_obj,
            'cat': cat,
            'sizes': sizes,
            'colors': colors,
            'user_firstname': user_detail.user_firstname,
            'user_image': user_detail.user_image,
            'user': user_detail,
            'cat_name': cat_name,
            'size_id': size_id,
            'color_id': color_id,
            'min_prize': min_prize,
            'max_prize': max_prize,
            
        }
        return render(request, 'store/user_store.html', context)
    else:
        return redirect('user_login')
    
    
@never_cache
def product_detail(request, id):
    # if 'user_email' in request.session:
    try:
        single_product = get_object_or_404(Product, id=id)
        
        print(single_product.product_discount)
        print(single_product.price)
        print(single_product.category.offer_active)
        print(single_product.offer_active)
        
        
        
        reviews = ReviewRating.objects.filter(product=single_product)
        cat=Category.objects.all()
        # print(id,single_product)
        variants = Variation.objects.filter(product=single_product)
        colors=[]
        sizes=[]
        # product_gallery = []
        for prod in variants:
            if prod.color not in colors:
                # print(prod.color)
                colors.append(prod.color)
            if prod.size not in sizes:
                sizes.append(prod.size)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    product_gallery = ProductGallery.objects.filter(product__product=single_product)
    if 'user_email' in request.session:
        user = UserDetail.objects.get(user_email=request.session['user_email'])
        try:
            ord_pdt = False
            for pdt in variants:
                ordr = Order.objects.filter(user=user, product=pdt).exists()
                if ordr:
                    ord_pdt = True
            # print(ord_pdt)
        except Order.DoesNotExist:
            ord_pdt = False
        # Get the reviews
        context = {
            'cat': cat,
            'single_product': single_product,
            'product_gallery': product_gallery,
            'variants':variants,
            'ord_pdt':ord_pdt,
            'reviews': reviews,
            'colors': colors,
            'sizes': sizes,
            'user_firstname': user.user_firstname,
            'user_image': user.user_image,
            'user': user
        }
    else:
        context = {
        'cat': cat,
        'single_product': single_product,
        'product_gallery': product_gallery,
        'variants':variants,
        'reviews': reviews,
        'colors': colors,
        'sizes': sizes,
        }
    return render(request, 'store/product_detail.html', context)

@never_cache
def user_dashboard(request):
    if 'user_email' in request.session:
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        order_pdt= Order.objects.filter(user=user_detail)
        orders_count = order_pdt.count()
        cat=Category.objects.all()
            
        context = {
            'cat':cat,
            'orders_count':orders_count,
            'user':user_detail,
            'user_image': user_detail.user_image,
            'user_firstname': user_detail.user_firstname,
            }
        # print(user_detail.id)
        return render(request, 'accounts/user_dashboard.html',context)
    else:
        return redirect('user_login')


@never_cache
def user_profile_info(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        # print(user_email)
        cat=Category.objects.all()
        user = UserDetail.objects.get(user_email=user_email)
        adrs = Address.objects.filter(user=user).all()
        context = {
            'cat':cat,
            'user':user,
            'user_image':user.user_image,
            'user_firstname': user.user_firstname,
            'adrs':adrs,}
        return render(request, 'accounts/user_profile_information.html',context)
    else:
        return redirect('user_login')
@never_cache
def edit_personal_info(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            user_firstname = request.POST.get('firstname')
            user_lastname = request.POST.get('lastname')
            UserDetail.objects.filter(user_email=user.user_email).update(user_firstname=user_firstname,user_lastname=user_lastname)
            messages.success(request, 'User personal information updated successfully')
            return redirect('user_profile_info')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')

@never_cache
def edit_email(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            try:
                user_email = request.session['user_email']
                user = UserDetail.objects.get(user_email=user_email)
            except UserDetail.DoesNotExist:
                messages.warning(request,'invalid user')
            new_email = request.POST.get('email')
            
            request.session['new_email'] = new_email
            return redirect('verify_edit_email')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')


class EmailChangeVerification(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'new_email' and 'user_email' in request.session:
            user_email = request.session['user_email']
            cat = Category.objects.all()
            user = UserDetail.objects.get(user_email=user_email)
            context = {
                'cat':cat,
                'user':user,
                'user_image':user.user_image,
                'user_firstname': user.user_firstname,
                }
            return render(request, 'accounts/change_email_verification.html',context)
        else:
            return redirect('edit_email')
        
    @method_decorator(never_cache)
    def post(self, request):
        if 'new_email' and 'user_email' not in request.session:
            return redirect('edit_email')
        user_pass = request.POST.get('password')
        user_cpass = request.POST.get('c_password')
        
        new_email = request.session['new_email']
        user_email = request.session['user_email']

        if user_pass == user_cpass:
            user = UserDetail.objects.filter(user_email=user_email)
            user.update(user_email=new_email)
            
            del request.session['user_email']
            request.session['user_email'] = new_email
            del request.session['new_email']
            
            messages.success(request,'Successfully changed your email address.')
            return redirect('edit_email')
        else:
            messages.warning(request, 'Passwords not match.')
            return redirect('verify_edit_email')
        
        
@never_cache
def edit_phone(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            user_phone = request.POST.get('phone')
            UserDetail.objects.filter(user_email=user.user_email).update(user_phone=user_phone)
            messages.success(request, 'User mobile number updated successfully')
            return redirect('user_profile_info')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')
    
@never_cache
def edit_image(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)

            if 'image' in request.FILES:
                uploaded_image = request.FILES['image']

                # Delete the old image if it exists
                if user.user_image:
                    user.user_image.delete()

                # Update the user's image field in the model
                user.user_image = uploaded_image
                user.save()

                messages.success(request, 'User image updated successfully')
            else:
                messages.warning(request, 'Please select an image to upload')

            return redirect('user_profile_info')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')
        
        
@never_cache
def user_manage_address(request):
    if 'user_email' in request.session:
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        adrs = Address.objects.filter(user=user_detail).all()
        cat=Category.objects.all()
        context = {
            'cat':cat,
            'user':user_detail,
            'user_image':user_detail.user_image,
            'user_firstname': user_detail.user_firstname,
            'adrs':adrs,}
        for i in adrs:
            print(i)
        return render(request, 'accounts/user_mange_address.html', context)
    else:
        return redirect('user_login')
@never_cache
def add_address(request):
    if 'user_email' in request.session:
        if request.method=='POST':
            form = UserAddressForm(request.POST)
            if form.is_valid():
                user = UserDetail.objects.get(user_email = request.session['user_email'])
                reg = form.save(commit=False)
                reg.user = user
                reg.save()
                messages.success(request, 'new address added successfully')
                return redirect('user_manage_address') 
            else:
                return redirect('add_address') 
                # return render(request, 'accounts/user_add_address.html', {'form': form})
        else:
            form = UserAddressForm()
            user = UserDetail.objects.get(user_email=request.session['user_email'])
            cat=Category.objects.all()
            context = {
            'cat':cat,
            'user':user,
            'user_image':user.user_image,
            'user_firstname': user.user_firstname,
            'form': form,
            }
            return render(request, 'accounts/user_add_address.html', context)
    else:
        return redirect('user_login')
    
@never_cache
def edit_address(request, id):
    if 'user_email' in request.session:
        adrs = Address.objects.get(id=id)
        if request.method == 'POST':
            form = UserAddressForm(request.POST, instance=adrs)
            if form.is_valid():
                form.save()
                messages.success(request,"Your address is now updated")
                return redirect('user_manage_address')
            else:
                return render(request, 'accounts/user_edit_address.html', {'form': form,'adrs':adrs})
        else:
            form = UserAddressForm(instance=adrs)
            return render(request, 'accounts/user_edit_address.html', {'form': form,'adrs':adrs})
    else:
        return redirect('user_login')

@never_cache
def delete_address(request):
    if 'user_email' in request.session:
        aid=request.GET['aid']
        Address.objects.filter(id=aid).delete()
        return redirect('user_manage_address')
    else:
        return redirect('admin_login')


class ChangePasswordView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'user_email' in request.session:
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            cat=Category.objects.all()
            context={
                'cat': cat,
                'user_firstname': user.user_firstname,
                'user_image': user.user_image,
             }
            return render(request,'accounts/change_password.html',context)
        else:
            return redirect('user_login')
    @method_decorator(never_cache) 
    def post(self, request):
        if 'user_email' in request.session:
            user = UserDetail.objects.get(user_email=request.session['user_email'])
            password = request.POST.get('old_password')
            pass1 = request.POST.get('new_pass1')
            pass2 = request.POST.get('new_pass2')
            if check_password(password, user.user_password):
            # if user.user_password == password:
                if pass1 == pass2 and pass1 != password:
                    user.user_password = make_password(pass1)  # Hash the password
                    user.save()
                    messages.success(request, "Passwords changed successfully")
                    return redirect('user_profile_info')
                else:
                    messages.warning(request, "Passwords not matching")
            else:
                messages.warning(request, "Incorrect password")
            return redirect('change_password')
        else:
            return redirect('user_login')
        
@never_cache
def forgot_password(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            try:
                email = request.POST.get('email')
                user = UserDetail.objects.get(user_email=email)
                # print(user.user_firstname)
            except:
                messages.warning(request,'No user is registered with this email address')
                return redirect('forgot_password')
            """send otp code for mail"""
            o=str(user.user_firstname)+generateOTP()
            # print(o)
            # user.user_password = make_password(o)
            # user.save()
            # print(o)
            # print(user.user_password)
            if user:
                htmlgen =  f'<p>Your new password for login Celeritas account is <strong>{o}</strong></p>.Its just a recovery password please change the password after login.'
                email_sent = send_mail('OTP request',o,'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
                if email_sent:
                    print(email_sent)
                    print(o)
                    user.user_password = make_password(o)
                    user.save()
                    # Email was sent successfully
                    del request.session['user_email']
                    messages.success(request,'Please check your email for new password and login again')
                    return redirect('forgot_password')
                else:
                    # Email sending failed
                    messages.warning(request, 'Email sending failed. Not a proper email Please try again.')
                    return redirect('forgot_password')
            else:
                messages.warning(request,'No user is registered with this email address')
                return redirect('forgot_password')
        else:
            cat=Category.objects.all()
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            # print(o)
            context={
                'cat': cat,
                'user_firstname': user.user_firstname,
                'user_image': user.user_image,
             }
            return render(request,'accounts/forgot_password.html',context)
    else:
        return redirect('user_login')
    
@never_cache
def forgot_pass_logout_user(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            user = UserDetail.objects.get(user_email=email)
            print(user.user_firstname)
        except:
            messages.warning(request,'No user is registered with this email address')
            return redirect('forgot_pass_out_user')
        
        o=str(user.user_firstname)+generateOTP()
        # print(o)
        # user.user_password = make_password(o)
        # user.save()
        
        """send otp code for mail"""
        if user:
            htmlgen =  f'<p>Your new password for login Celeritas account is <strong>{o}</strong></p>.Its just a recovery password please change the password after login.'
            email_sent = send_mail('OTP request',o,'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
            if email_sent:
                print(o)
                user.user_password = make_password(o)
                user.save()
                # Email was sent successfully
                messages.success(request, 'Please check your email for a new password')
                return redirect('user_login')
            else:
                # Email sending failed
                messages.warning(request, 'Email sending failed. Not a proper email Please try again.')
                return redirect('forgot_pass_out_user')
            # # del request.session['user_email']
            # messages.success(request,'Please check your email for new password')
            # return redirect('user_login')
        else:
            messages.warning(request,'No user is registered with this email address')
            return redirect('forgot_pass_out_user')
    else:
        cat=Category.objects.all()
        context={
            'cat': cat,
         }
        return render(request,'accounts/forgot_password_out.html',context)

        
@never_cache
def orders(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        user = UserDetail.objects.get(user_email = user_email)
        
        ord = Order.objects.filter(user=user).order_by('-id')
        cat = Category.objects.all()
        paginator = Paginator(ord, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
                'page_obj': page_obj,
                'cat':cat,
                'user_firstname': user.user_firstname,
                'user_image': user.user_image,
                'user':user,
            }
        if ord.exists():
            return render(request,'accounts/orders.html',context)
        else:
            messages.warning(request,'No orders yet')
            return render(request,'accounts/orders.html',context)
    else:
        return redirect('user_login')
@never_cache
def view_order(request,id):
    if 'user_email' in request.session:
        try:
            order_pdt = Order.objects.get(id=id)
        except Order.DoesNotExist:
            messages.error(request,"No Product found")
            return redirect('orders')
        cat = Category.objects.all()
        context = {
                'order_pdt': order_pdt,
                'cat':cat,
                'user_firstname': order_pdt.user.user_firstname,
                'user_image': order_pdt.user.user_image,
                'user':order_pdt.user,
            }
        return render(request,'accounts/view_order.html',context)
    else:
        return redirect('user_login')
    
@never_cache
def cancel_order(request,id):
    if 'user_email' in request.session:
        user_email = request.session['user_email'] 
        order = Order.objects.filter(id=id).first()
        if order.order_type == 'Cash on delivery':
            Order.objects.filter(id=id).update(status='Cancel Requested')
            return redirect('view_order', id=id)
        try:
            wallet = Wallet.objects.get(user__user_email = user_email )
        except Wallet.DoesNotExist:
            messages.warning(request,'Please activate your wallet to apply for cancellation')
            return redirect('view_order', id=id)
        if wallet.is_active:
            Order.objects.filter(id=id).update(status='Cancel Requested')
            return redirect('view_order', id=id)
        else:
            messages.warning(request,'Complete your wallet activation to applying for cancellation.')
            return redirect('view_order', id=id)
    else:
        return redirect('user_login')

@never_cache
def return_order(request,id):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        try:
            user = UserDetail.objects.get(user_email = user_email)
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            messages.warning(request,'Please activate your wallet to apply for return')
            return redirect('view_order', id=id)
        if wallet.is_active:
            Order.objects.filter(id=id).update(status='Return Requested')
            return redirect('view_order', id=id)
        else:
            messages.warning(request,'Complete your wallet activation for apply return.')
            return redirect('view_order', id=id)
    else:
        return redirect('user_login')
    
@never_cache
def coupons(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        user = UserDetail.objects.get(user_email = user_email)
        cat = Category.objects.all()
        coupons = UserCoupon.objects.filter(user=user)
        paginator = Paginator(coupons, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj':page_obj,
            # 'coupons': coupons,
            'cat':cat,
            'user_firstname': user.user_firstname,
            'user_image': user.user_image,
            'user':user,
            }
        if coupons.exists():
            return render(request, 'accounts/user_coupons.html',context)
        else:
            messages.warning(request,'No Coupons Found')
            return render(request, 'accounts/user_coupons.html',context)
    else:
        return redirect('user_login')


@never_cache
def apply_coupon(request):
    if 'user_email' in request.session:     
        if request.method == 'POST':
            user_email = request.session['user_email']
            try:
                coup_code = request.POST.get('c_code')
                coupon = Coupon.objects.get(coupon_code__iexact=coup_code, is_active=True)
                cart = CartItem.objects.filter(cart__user__user_email=user_email)
                if cart.exists():
                    total = 0
                    quantity = 0
                    for cart_item in cart:
                        total += cart_item.subtotal
                        quantity += cart_item.quantity
                    grand_total = total
            except:
                messages.warning(request, 'No coupon')
                return redirect('proceed_to_checkout')
            
            if coup_code == coupon.coupon_code and coupon.is_active:
                if grand_total >= coupon.minimum_amount:
                    print(coupon.is_active)
                    UserCoupon.objects.filter(user__user_email=user_email).update(applied=False)
                    user_coupon = UserCoupon.objects.filter(user__user_email=user_email, coupon__is_active=True, coupon=coupon)
                    user_coupon.update(applied=True)
                    
                    if len(user_coupon) >0:
                        request.session['user_coupon'] = True
                        messages.success(request, 'Coupon Applied')
                    else:
                        messages.warning(request, 'No such coupon is available')
                        # return redirect('proceed_to_checkout')
                    
                    # cartcount = cart.count()
                    # for c in cart:
                        # Calculate new subtotal after applying discount to each cart item
                        # new_subtotal = c.subtotal - (discount / cartcount)
                    # messages.success(request, 'Coupon Applied')
                else:
                    messages.warning(request, f'Total amount should be grater than {coupon.minimum_amount}')
            elif coup_code == coupon.coupon_code:
                messages.warning(request, 'Coupon has expired')
            else:
                messages.warning(request, 'Coupon is not valid')
            
            return redirect('proceed_to_checkout')
        else:
            return redirect('proceed_to_checkout')
            
    else:
        return redirect('admin_login')
    
@never_cache
def cancelcoupon(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        UserCoupon.objects.filter(user__user_email=user_email,applied=True).update(applied=False)
        messages.warning(request,'Coupon removed')
        return redirect('proceed_to_checkout')
    else:
        return redirect('user_login')

@never_cache
def generate_invoice(request):
    if 'user_email' in request.session:
        user = UserDetail.objects.get(user_email=request.session['user_email'])
        
        ordered_product = Order.objects.get(Q(id=request.GET.get('ord_id')) & Q(user=user))
        data = {
            'date' : datetime.date.today(),
            'orderid': ordered_product.id,
            'ordered_date': ordered_product.ordered_date,
            'name': ordered_product.address.name,
            # 'email':ordered_product.user.user_email,
            'housename': ordered_product.address.housename,
            'locality': ordered_product.address.locality,
            'city': ordered_product.address.city,
            'state': ordered_product.address.state,
            'zipcode': ordered_product.address.zipcode,
            'phone': ordered_product.address.phone,
            'product': ordered_product.product,
            'quantity': ordered_product.quantity,
            'amount': ordered_product.amount,
            # 'single_amount': ordered_product.product.product.price,
            'ordertype': ordered_product.order_type,
        }
        template_path = 'invoicepdf.html'
        html = render_to_string(template_path, data)

        # Create a Django response object with content type as PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{data["orderid"]}.pdf"'

        # Create a PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse('We had some errors generating the PDF')
        
        return response
    else:
        return redirect('user_login')
    
def generateOTP() :
    digits = "0123456789"
    OTP = ""
    for _ in range(6) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

@never_cache
def otp_login(request):
    if request.method == 'POST':
        try:
            phone = int(request.POST.get('phone'))
            user = UserDetail.objects.get(user_phone=phone)
            print(user)
        except:
            messages.warning(request,'No user is registered with this mobile number')
            return redirect('otp_login')
        print(phone)
        o=str(user.user_firstname)+generateOTP()
        print(o)
        request.session['otp'] = o
        request.session['random _data'] = phone
        print('otp is ',o)
        account_sid = 'AC61ecfa87d2c06f591728efd8db170078'
        auth_token = 'c1719b983d826bf556d2c91776a7babe'
        TWILIO_PHONE_NUMBER = +16562184391
        
        client = Client(account_sid, auth_token)
        to_phone_number = phone
        
        message = client.messages.create(
            body=f'Your OTP for login Celeritas account is: {o}',
            from_= TWILIO_PHONE_NUMBER,
            to='+91' + str(to_phone_number)
        )
        
        """send otp code for mail"""
        if user:
            htmlgen =  f'<p>Your OTP for login Celeritas account is <strong>{o}</strong></p>'
            send_mail('OTP request',o,'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
            # messages.success(request,'Please check your email for OTP verification')
            
        messages.success(request,'Please check your email and sms for OTP verification')
        return render(request, "accounts/otp.html", {'phone': phone})
    else:
        return render(request ,"accounts/user_otplogin.html")

@never_cache
def otp_verification(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == request.session["otp"]:
            user_phone=request.session.get('random _data')
            print(user_phone)
            try:
                user = UserDetail.objects.get(user_phone=user_phone)
                print(user)
            except:
                messages.warning(request,'No user is registered with this mobile number')
                return redirect('otp_login')
            if user:
                request.session['user_email'] = user.user_email
                del request.session['random _data']
                return redirect('user_home')
            else:
                messages.warning(request,'User not found')
                return redirect('otp_login')
        else:
            messages.warning(request,'Entered OTP is wrong please try agin')
            return redirect('otp_login')
    else:
        messages.warning(request,'Something went wrong please try agin')
        return redirect('otp_login')
    
@never_cache
def submit_review(request,id):
    if 'user_email' in request.session:
        url = request.META.get('HTTP_REFERER')
        if request.method == 'POST':
            try:
                prod = Product.objects.get(id=id)
                user=UserDetail.objects.get(user_email=request.session['user_email'] )
                reviews = ReviewRating.objects.get(user=user, product=prod)
                form = ReviewForm(request.POST, instance=reviews)
                form.save()
                messages.success(request, 'Thank you your review has been updated.')
                return redirect(url)
            except ReviewRating.DoesNotExist:
                form = ReviewForm(request.POST)
                if form.is_valid():
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.rating = form.cleaned_data['rating']
                    data.review = form.cleaned_data['review']
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.product = prod
                    data.user = user
                    data.save()
                    messages.success(request, 'Thank you your review has been submited.')
                    return redirect(url)
    else:
        return redirect('user_login')
                    

def my_wallet(request):
    if 'user_email' in request.session:
        try:
            user = UserDetail.objects.get(user_email = request.session['user_email'])
        except UserDetail.DoesNotExist:
            messages.warning(request,'User Not Found')
            return redirect('my_wallet')
        wallet = Wallet.objects.filter(user=user)
        if wallet.exists():
            wallet = wallet.first()
            if wallet.is_active:
                print(wallet.is_active)
            else:
                print('not activated')
            cat = Category.objects.all()
            context = {
                'cat':cat,
                'user_firstname': user.user_firstname,
                'user_image': user.user_image,
                'user':user,
                'wallet':wallet,
                }
            return render(request, 'accounts/my_wallet.html',context)
        else:
            Wallet.objects.create(user=user)
            print("Wallet not exists")
            return redirect('my_wallet')
        
    else:
        return redirect('user_login')
    
    
    
def add_wallet(request):
    if 'user_email' in request.session:
        try:
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
        except UserDetail.DoesNotExist:
            messages.warning(request, 'User Not Found')
            return redirect('my_wallet')

        wallet = Wallet.objects.get(user=user)

        if request.method == 'POST':
            form = WalletTransactionForm(request.POST, request.FILES)
            pass1 = request.POST.get('password')
            pass2 = request.POST.get('c_password')

            if form.is_valid():
                if pass1 == pass2:
                    if check_password(pass1, user.user_password):
                        amount = form.cleaned_data['amount']
                        currency = form.cleaned_data['currency']
                        # form.save()
                        wallet.deposit(amount, currency,type='Deposit')
                        messages.success(request, "Amount added to your wallet")
                        return redirect('my_wallet')
                    else:
                        messages.warning(request, "Wrong Password")
                        return redirect('add_wallet')
                else:
                    messages.warning(request, "Passwords not matching")
                    return redirect('add_wallet')
            else:
                messages.warning(request, "Form is not valid")
                return redirect('add_wallet')
        else:
            form = WalletTransactionForm()

        context = {
            'user_firstname': user.user_firstname,
            'user_image': user.user_image,
            'user': user,
            'form': form,
        }

        return render(request, "accounts/add_wallet.html", context)
    else:
        return redirect('user_login')


def activate_wallet(request):
    if 'user_email' in request.session:
        try:
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
        except UserDetail.DoesNotExist:
            messages.warning(request, 'User Not Found')
            return redirect('activate_wallet')
        if request.method == 'POST':
            password = request.POST.get('password')
            c_password = request.POST.get('c_password')
            if password == c_password:
                if check_password(password,user.user_password):
                    Wallet.objects.filter(user=user).update(is_active=True)
                    messages.success(request, "Successfully activated your wallet and you have 200 bonus wallet amount.")
                    return redirect('my_wallet')
                else:
                    messages.warning(request, "Wrong Password.")
                    return redirect('activate_wallet')
            else:
                messages.warning(request, "Passwords not matching")
                return redirect('activate_wallet')
        else:
            cat = Category.objects.all()
            context = {
                'user_firstname': user.user_firstname,
                'user_image': user.user_image,
                'user': user,
                'cat': cat,
            }
            return render(request,'accounts/activate_wallet.html',context)
    else:
        return redirect('user_login')

@never_cache
def show_trans_history(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        try:
            wallet = Wallet.objects.get(user__user_email=user_email)
        except Wallet.DoesNotExist:
            messages.warning(request,'No wallet found')
            return redirect('my_wallet')
        trans_hist = wallet.get_transaction_history()
        cat = Category.objects.all()
        
        paginator = Paginator(trans_hist, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # print(trans_hist)
        context = {
            'user_firstname': wallet.user.user_firstname,
            'user_image': wallet.user.user_image,
            'user': wallet.user,
            'cat': cat,
            'trans_hist': trans_hist,
            'page_obj' : page_obj,
        }
        return render(request, 'accounts/transaction_history.html',context)
    else:
        return redirect('user_login')                  

@never_cache             
def handle_not_found(request,exception):
    return render(request,'not_found.html')
                    
                    
                