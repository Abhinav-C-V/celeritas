from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, HttpResponse ,Http404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.views.generic import View
from celeritas.forms.user_form import UserSignupForm, UserLoginForm, UserAddressForm
from category.models import Category
from product.models import Product, ProductGallery, Variation, Size, Color
from cart.models import Wishlist, Cart, CartItem, Coupon, UserCoupon
from .models import UserDetail, Address
from admn.models import  Banner

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
# from django.http import JsonResponse
# from .forms import UserSignupForm

# from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from cart.models import Order
from xhtml2pdf import pisa
from django.db.models import Q
import datetime
# from .models import UserDetail, Order
# from django.contrib import messages
# from .models import UserDetail  # You need to import your UserDetail model
import uuid  # Import the UUID module
from .utils import generate_reset_token  # Import the function from step 1






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
            details3= Product.objects.filter(category__id=cat_id).order_by('id')
        elif prod is not None and cat_id is None:
            details3= Product.objects.filter(name__icontains=prod).order_by('id')    
        elif prod is not None and cat_id is not None:
            details3= Product.objects.filter(name__icontains=prod,category__id=cat_id).order_by('id')
        else:
            details3=Product.objects.all().order_by('id')
        paginator = Paginator(details3, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        obj = Banner.objects.all()
        return render(request, 'index.html',{ 'page_obj': page_obj, 'cat':cat, 'obj':obj})

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

# def index(request):
#     return render(request, 'home.html')

class UserLoginView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'user_email' in request.session:
            return redirect('user_home')
        else:
            form = UserLoginForm()
            return render(request, 'accounts/user_login.html', {'form': form})
    
    @method_decorator(never_cache)
    def post(self, request):
        user_email = request.POST.get('user_email')
        password = request.POST.get('user_password')
        user = UserDetail.objects.filter(user_email=user_email).first()
        if user and user.user_is_active is True:
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
    def get(self, request):
        if 'user_email' in request.session:
            return redirect('home_store')
        form = UserSignupForm()
        return render(request, 'accounts/user_register.html', {'form': form})
    
    def post(self, request):
        if 'user_email' in request.session:
            return redirect('home_store')
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            password = request.POST.get('user_password')
            c_password = request.POST.get('user_cpassword')
            if c_password == password:
                user = form.save(commit=False)
                user.user_password = make_password(password)  # Hash the password
                user.save()
                return redirect('user_login')
            else:
                messages.warning(request, "Passwords do not match")
                return redirect('user_register')
        else:
            return render(request, 'accounts/user_register.html', {'form': form})



        
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if UserDetail.objects.filter(user_email=email).exists():
            user = UserDetail.objects.get(user_email__exact=email)
            # Generate a reset token
            reset_token = generate_reset_token()
            
            # Save the reset token to the user model
            user.reset_token = reset_token
            # print(user.reset_token)
            # print(reset_token)
            # print(user)
            
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            print(current_site)
            
            message = render_to_string('accounts/reset_password_email.html',{
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': reset_token,  # Pass the reset token
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to = [to_email])
            # print(send_email)
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address .' )
            return redirect('user_login')
        else:
            messages.warning(request, 'Account does not exits.')
            return redirect('forgot_password')
            
    else:    
        return render(request, 'accounts/forgot_password.html')
    
    
    
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserDetail._default_manager.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, UserDetail.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please Reset Your Password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('user_login')
    
def reset_password(request):
    return render(request, 'accounts/user_resetPassword.html',)





@never_cache
def userlogout(request):
    if 'user_email' in request.session:
        del request.session['user_email']
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
        paginator = Paginator(details3, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        obj = Banner.objects.all()
        print(len(obj))
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        
        context = {
            'page_obj': page_obj,
            'cat':cat,
            'obj':obj,
            'user_firstname': user_detail.user_firstname,
            'user_image': user_detail.user_image,
            'user':user_detail,
        }
        return render(request, 'store/user_home.html', context)
    else:
         return redirect('user_login')
     
     
@never_cache
def userstore(request):
    if 'user_email' in request.session: 
        cat=Category.objects.all()
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        sizes = Size.objects.all()
        colors = Color.objects.all()
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
        paginator = Paginator(details3, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # product_count = Product.objects.all().count()
        # print(sizes)
        context = {
            'page_obj': page_obj,
            'cat':cat,
            'sizes':sizes,
            'colors': colors,
            'user_firstname': user_detail.user_firstname,
            'user_image': user_detail.user_image,
            'user':user_detail,
        }
        return render(request, 'store/user_store.html', context)
    else:
         return redirect('user_login')
     
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
        
        paginator = Paginator(details3, 6)
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
        }
        return render(request, 'store/user_store.html', context)
    else:
        return redirect('user_login')
    
    
@never_cache
def product_detail(request, id):
    # if 'user_email' in request.session:
    try:
        
        single_product = get_object_or_404(Product, id=id)
        # print(id,single_product)
        variants = Variation.objects.filter(product=single_product)
        colors=[]
        sizes=[]
        for prod in variants:
            if prod.color not in colors:
                print(prod.color)
                colors.append(prod.color)
            if prod.size not in sizes:
                sizes.append(prod.size)
        # for clr in variants.color:
        #     print(clr)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    product_gallery = ProductGallery.objects.filter(product__product=single_product)
    if 'user_email' in request.session:
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        context = {
            'single_product': single_product,
            'product_gallery': product_gallery,
            'variants ':variants,
            'colors': colors,
            'sizes': sizes,
            'user_firstname': user_detail.user_firstname,
            'user_image': user_detail.user_image,
            'user': user_detail
        }
    else:
        context = {
        'single_product': single_product,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def user_dashboard(request):
    if 'user_email' in request.session:
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        order_pdt= Order.objects.filter(user=user_detail)
        orders_count = order_pdt.count()
            
        context = {
            'orders_count':orders_count,
            'user':user_detail,
            'user_image': user_detail.user_image,
            'user_firstname': user_detail.user_firstname,
            }
        # print(user_detail.id)
        return render(request, 'accounts/user_dashboard.html',context)
    else:
        return redirect('user_login')



def user_profile_info(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        # print(user_email)
        user = UserDetail.objects.get(user_email=user_email)
        adrs = Address.objects.filter(user=user).all()
        context = {
            'user':user,
            'user_image':user.user_image,
            'user_firstname': user.user_firstname,
            'adrs':adrs,}
        return render(request, 'accounts/user_profile_information.html',context)
    else:
        return redirect('user_login')

def edit_personal_info(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            user_firstname = request.POST.get('firstname')
            user_lastname = request.POST.get('lastname')
            UserDetail.objects.filter(user_email=user.user_email).update(user_firstname=user_firstname,user_lastname=user_lastname)
            messages.success(request, 'User mobile number updated successfully')
            return redirect('user_profile_info')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')

        
def edit_email(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            user_email = request.POST.get('email')
            UserDetail.objects.filter(user_email=user.user_email).update(user_email=user_email)
            messages.success(request, 'User mobile number updated successfully')
            return redirect('user_logout')
        else:
            return redirect('user_profile_info')
    else:
        return redirect('user_login')
        
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
    
    
def edit_image(request):
    if 'user_email' in request.session:
        if request.method == 'POST':
            user_email = request.session['user_email']
            user = UserDetail.objects.get(user_email=user_email)
            # print("Form Data:", request.POST)
            # print("Files:", request.FILES)
            # Handle the uploaded image
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
        
        

def user_manage_address(request):
    if 'user_email' in request.session:
        user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
        adrs = Address.objects.filter(user=user_detail).all()
        context = {
            'user':user_detail,
            'user_image':user_detail.user_image,
            'user_firstname': user_detail.user_firstname,
            'adrs':adrs,}
        for i in adrs:
            print(i)
        return render(request, 'accounts/user_mange_address.html', context)
    else:
        return redirect('user_login')
    
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
                return render(request, 'accounts/user_add_address.html', {'form': form})
        else:
            form = UserAddressForm()
            return render(request, 'accounts/user_add_address.html', {'form': form})
    else:
        return redirect('user_login')
    
    
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


def delete_address(request):
    if 'user_email' in request.session:
        aid=request.GET['aid']
        Address.objects.filter(id=aid).delete()
        return redirect('user_manage_address')
    else:
        return redirect('admin_login')


class ChangePasswordView(View):
    def get(self, request):
        if 'user_email' in request.session:   
            return render(request,'accounts/change_password.html')
        else:
            return redirect('user_login')   
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
    
def cancel_order(request,id):
    if 'user_email' in request.session: 
        Order.objects.filter(id=id).update(status='Cancel Requested')
        return redirect('orders')
    else:
        return redirect('user_login')

def return_order(request,id):
    if 'user_email' in request.session: 
        Order.objects.filter(id=id).update(status='Return Requested')
        return redirect('orders')
    else:
        return redirect('user_login')
    
    
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
            except:
                messages.warning(request, 'No coupon')
                return redirect('proceed_to_checkout')
            
            if coup_code == coupon.coupon_code and coupon.is_active:
                UserCoupon.objects.filter(user__user_email=user_email).update(applied=False)
                UserCoupon.objects.filter(user__user_email=user_email, coupon__is_active=True, coupon=coupon).update(applied=True)
                
                try:
                    coup = UserCoupon.objects.get(user__user_email=user_email, coupon__is_active=True, applied=True)
                    discount = coup.coupon.discount_price
                except UserCoupon.DoesNotExist:
                    discount = 0
                
                cartcount = cart.count()
                for c in cart:
                    # Calculate new subtotal after applying discount to each cart item
                    new_subtotal = c.subtotal - (discount / cartcount)
                    print(new_subtotal)
                
                messages.success(request, 'Coupon Applied')
            elif coup_code == coupon.coupon_code:
                messages.warning(request, 'Coupon has expired')
            else:
                messages.warning(request, 'Coupon is not valid')
            
            return redirect('proceed_to_checkout')
        else:
            return redirect('proceed_to_checkout')
            
    else:
        return redirect('admin_login')
    
    
def cancelcoupon(request):
    user_email = request.session['user_email']
    UserCoupon.objects.filter(user__user_email=user_email).update(applied=False)
    messages.warning(request,'Coupon removed')
    return redirect('proceed_to_checkout')



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