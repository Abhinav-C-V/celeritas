from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, HttpResponse ,Http404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.views.generic import View
from celeritas.forms.user_form import UserSignupForm, UserLoginForm
from category.models import Category
from product.models import Product, ProductGallery, Variation
from .models import Wishlist, Cart, CartItem, Order, Coupon, UserCoupon
from home_store.models import UserDetail, Address
from admn.models import Banner
from django.db.models import Q, F
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect
from django.urls import reverse 
# from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
# from django.http import JsonResponse
# from django.contrib import messages
# from .forms import UserSignupForm
# from django.contrib import messages
from django.core.mail import send_mail
import razorpay
import random
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from home_store.views import generateOTP
# Create your views here.


@never_cache
def wishlist(request):
    if 'user_email' in request.session:
        wish_id = request.GET.get('prod_id')
        if wish_id is not None:
            wish_product = Variation.objects.filter(product=wish_id).first()
            pdt = Wishlist.objects.filter(user__user_email=request.session['user_email'], product=wish_product.product).first()
            if pdt is None:
                user_email = request.session.get('user_email')
                user_detail = get_object_or_404(UserDetail, user_email=user_email)
                wish = Wishlist(user=user_detail, product=wish_product.product)
                wish.save()
                messages.success(request, 'Item added to wishlist')
            else:
                messages.warning(request, 'Item is already in the wishlist')
        
        user_email = request.session.get('user_email')
        user_detail = get_object_or_404(UserDetail, user_email=user_email)
        wish_items = Wishlist.objects.filter(user=user_detail).order_by('-id')
        cat=Category.objects.all()
        
        if wish_items.exists():
            context = {
                'wish_items': wish_items,
                'user_firstname': user_detail.user_firstname,
                'user_image': user_detail.user_image,
                'user': user_detail,
                'cat':cat,
                
            }
            return render(request, 'store/wishlist.html', context)
        else:
            # messages.warning(request, 'No items in wishlist')
            context = {
                'user_firstname': user_detail.user_firstname,
                'user_image': user_detail.user_image,
                'user': user_detail,
                'cat':cat,
            }
            return render(request, 'store/wishlist.html', context)

    else:
        return redirect('user_login')

def remove_wishlist(request, id):
    if 'user_email' in request.session:
        Wishlist.objects.filter(id=id).delete()
        return redirect('wishlist')
    else:
        return redirect('user_login')
    
# @transaction.atomic
def add_to_cart(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        user = UserDetail.objects.get(user_email=user_email)
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user)

        try:
            prod_id = request.GET.get('product_id')
            if not prod_id:
                return redirect('product_detail', id=prod_id)
        except:
            return redirect('product_detail', id=prod_id)

        # Check if variant with color and size combination is available
        try:
            color = request.POST.get('color')
            size = request.POST.get('size')

            variant = Variation.objects.get(product=prod_id, color=color, size=size)
            # print(variant.stock)
            if variant.stock < 1:
                messages.warning(request, 'Out of stock')
                return redirect('product_detail', id=prod_id)

            try:
                cart_item = CartItem.objects.get(cart=cart, product=variant)
                cart_item.quantity += 1
                variant.stock -= 1
                variant.save()
                cart_item.save()
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=cart, product=variant, quantity=1)
                variant.stock -= 1
                variant.save()
                cart_item.save()

        except Variation.DoesNotExist:
            messages.warning(request, 'Variant not available')
            return redirect('product_detail', id=prod_id)

        return redirect('cart')
    else:
        messages.warning(request, 'Please login first')
        return redirect('user_login')




@never_cache
def cart(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        # prod_id = request.GET.get('product_id')
        user_detail = UserDetail.objects.get(user_email=user_email)
        cat=Category.objects.all()
        
        try:
            cart = Cart.objects.get(user=user_detail)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user_detail)
        
        cart_items = CartItem.objects.filter(cart=cart)
        if cart_items.exists():
            total = 0
            quantity = 0
            for cart_item in cart_items:
                total += cart_item.subtotal
                quantity += cart_item.quantity
            # tax = (total*1.7)/100
            tax = 0
            grand_total = total + tax
            
            context = {
                'cart_items': cart_items,
                'total': total,
                'quantity': quantity,
                'tax': tax,
                'grand_total' : grand_total,
                'user_firstname': user_detail.user_firstname,
                'user_image': user_detail.user_image,
                'user':user_detail,
                'cat':cat,
                
            }
            return render(request, 'store/cart.html', context)
        else:
            user_detail = UserDetail.objects.get(user_email=request.session['user_email'])
            context = {
                'user_firstname': user_detail.user_firstname,
                'user_image': user_detail.user_image,
                'user':user_detail,
                'cat':cat,
                
            }
            # messages.warning(request, 'No items in cart')
            return render(request, 'store/cart.html',context)

    return redirect('user_login')
    
def remove_cart_item(request):
    if 'user_email' in request.session:
        id=request.GET['id']
        item=CartItem.objects.get(id=id)
        cart_quantity = item.quantity
        cart_product = item.product.product
        Variation.objects.filter(product=cart_product).update(stock=F('stock')+cart_quantity)
        CartItem.objects.filter(id=id).delete()
        return redirect('cart')
    else:
        return redirect('user_login')
    

def increment_cart_item(request):
    if 'user_email' in request.session:
        cart_id = request.GET.get('cart_id')
        cart_item = CartItem.objects.get(id=cart_id)
        if cart_item.product.stock != 0:
            if cart_item.quantity > 0 :
                cart_item.quantity += 1
                cart_item.product.stock -= 1
                cart_item.product.save()
                cart_item.save()
                print(cart_item.product.stock)
                print(cart_item.quantity)            
                return redirect('cart')
            else:
                CartItem.objects.filter(id=cart_id).delete()
                return redirect('cart')
        else:
            messages.warning(request, 'Out Of Stock')
            return redirect('product_detail', id=cart_item.product.product.id)
    else:
        return redirect('user_login')


def decrement_cart_item(request):
    if 'user_email' in request.session:
        cart_id = request.GET.get('cart_id')
        cart_item = CartItem.objects.get(id=cart_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.product.stock += 1
            cart_item.product.save()
            cart_item.save()
            print(cart_item.product.stock)
            print(cart_item.quantity)            
            return redirect('cart')
        else:
            cart_item.product.stock += 1
            cart_item.product.save()
            print(cart_item.product.stock)
            print(cart_item.quantity)
            CartItem.objects.filter(id=cart_id).delete()
            return redirect('cart')
    else:
        return redirect('user_login')
    
@never_cache
def proceed_to_checkout(request):
    if 'user_email' in request.session:
        user_email=request.session['user_email']
        # cart = CartItem.objects.filter(cart__user=user_detail).all()
        cat=Category.objects.all()
        user_detail = UserDetail.objects.get(user_email=user_email)
        adrs = Address.objects.filter(user=user_detail).all()
        selected_adrs = Address.objects.filter(user=user_detail,selected=True)
        if selected_adrs:
            print("hello",selected_adrs)
        else:
            print("no address")
        # print(len(adrs))
        cart = CartItem.objects.filter(cart__user=user_detail).all()
        if len(cart)<=0:
            return redirect('cart')
       
        # captcha = random.randint(111111,999999)
        captcha = generateOTP()
        
        # print(captcha)
        usercoupon = UserCoupon.objects.filter(user__user_email=user_email, coupon__is_active=True, applied=True).first()
        try:
            # usercoupon = UserCoupon.objects.get(user__user_email=user_email, coupon__is_active=True, applied=True)
            if usercoupon is not None:
                discount = usercoupon.coupon.discount_price
        except UserCoupon.DoesNotExist:
            discount = 0
        cartcount = cart.count()
        # usercoupon = UserCoupon.objects.filter(user__user_email=user_email, applied=True).first()
        if usercoupon:
            if cart.exists():
                total = 0
                quantity = 0
                for cart_item in cart:
                    total += cart_item.subtotal - (discount / cartcount)
                    quantity += cart_item.quantity
                grand_total = total
            else:
                total = 0
                quantity = 0
                grand_total = total
            usercoupon.applied = True
        else:
            if cart.exists():
                total = 0
                quantity = 0
                for cart_item in cart:
                    total += cart_item.subtotal
                    quantity += cart_item.quantity
                grand_total = total
            else:
                total = 0
                quantity = 0
                grand_total = total
            usercoupon = False
        # print(usercoupon)
        # tax = (total*1.7)/100
        # grand_total = total
        context = {
                'cat':cat,
                'user_firstname': user_detail.user_firstname,
                'user_image': user_detail.user_image,
                'user':user_detail,
                'adrs': adrs,
                'selected_adrs': selected_adrs,
                'cart': cart,
                # 'selected_ad': selected_ad,
                'quantity': quantity,
                'total': total,
                'grand_total':grand_total,
                # 'tax': tax,
                'captcha': captcha,
                'usercoupon': usercoupon,
            }
       
        return render(request, 'store/checkout.html', context)
    else:
        return redirect('user_login')


def select_address(request):
    if 'user_email' in request.session:
        user =UserDetail.objects.get(user_email=request.session['user_email'])
        ad_id = request.GET.get('ad_id')
        address = Address.objects.filter(user=user).all()
        print(address)
        for adrs in address:
            if adrs.selected is True:
                print(adrs)
                Address.objects.filter(id=adrs.id).update(selected=False)
                print(adrs)
            # print(adrs)
        Address.objects.filter(id=ad_id,user=user).update(selected=True)
        return redirect('proceed_to_checkout')
    else:
        return redirect('user_login')


def confirm_order(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        user = UserDetail.objects.get(user_email = user_email)
        try:
            user_ad = Address.objects.get(user=user,selected=True)
        except:
            messages.warning(request,'No address specified')
            return redirect('proceed_to_checkout')
        cart = CartItem.objects.filter(cart__user=user)
        try:
            coupon = UserCoupon.objects.get(user=user,coupon__is_active=True,applied=True)
            discount = coupon.coupon.discount_price
        except:
            discount = 0
        cartcount = cart.count()
        for c in cart:
            Order(user=user, address=user_ad, product=c.product, amount=c.subtotal-(discount)/cartcount).save()
            # c.delete()
            print("order placed cod")
        return render(request,'store/confirm_order.html')
    else:
        return redirect('user_login')

    
@never_cache
def cash_on_delivery(request):
    if 'user_email' in request.session:
        cat=Category.objects.all()
        user_email=request.session['user_email']
        if request.method == 'POST':
            user = UserDetail.objects.get(user_email = user_email)
            captcha = request.POST.get('captcha')
            c_captcha = request.POST.get('c_captcha')
            try:
                user_1 = Address.objects.get(user=user,selected=True)
            except:
                messages.warning(request,'No address specified')
                return redirect('proceed_to_checkout')
            if captcha == c_captcha:
                cart = CartItem.objects.filter(cart__user__user_email=user.user_email)
                try:
                    coupon = UserCoupon.objects.get(user=user,coupon__is_active=True,applied=True)
                    discount = coupon.coupon.discount_price
                except:
                    discount = 0
                cartcount = cart.count()
                for c in cart:
                    ord = Order(user=user, address=user_1, product=c.product, amount=c.subtotal-(discount)/cartcount, quantity=c.quantity )
                    ord.save()
                    htmlgen =  f'<p>Your Celeritas Order of Order ID <strong>ORDID{ord.id}</strong> placed successfully.</p>Price: ₹ {c.subtotal-(discount)/cartcount}<p>Quantity: {c.quantity} No.s</p>'
                    send_mail('Order Placed',str(ord.id),'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
                    # c.delete()
                UserCoupon.objects.filter(user__user_email=user_email,coupon__is_active=True,applied=True).delete()
                context = {
                    'cat':cat,
                    'user_firstname': user.user_firstname,
                    'user_image': user.user_image,
                    'user':user,
                    'cart': cart,
                    }
                return render(request,'store/confirm_order.html',context)
            else:
                messages.warning(request, 'please enter the digits carefully')
                return redirect('proceed_to_checkout')
        else:
            return redirect('proceed_to_checkout')
    else:
        return redirect('user_login')
    


def r_razorpay(request):
    if 'user_email' in request.session:
        user_email = request.session['user_email']
        user = UserDetail.objects.get(user_email = user_email)
        try:
            user_ad = Address.objects.get(user=user,selected=True)
        except:
            messages.warning(request,'No address specified')
            return redirect('proceed_to_checkout')
        cart = CartItem.objects.filter(cart__user=user)
        try:
            coupon = UserCoupon.objects.get(user=user,coupon__is_active=True,applied=True)
            discount = coupon.coupon.discount_price
        except:
            discount = 0
        cartcount = cart.count()
        client = razorpay.Client(auth=("rzp_test_FzpBcunlDun1vW", "0CmJy8RJrFXmVAsInbHBJSyr"))
        DATA = {
            "amount": 100,
            "currency": "INR",
            "receipt": "receipt#1",
            "payment_capture": 1,
            "notes": {
                "key1": "value3",
                "key2": "value2"
            }
        }

        razorpay_response=client.order.create(data=DATA)
        reazorpay_status=razorpay_response['status']
        
        print(reazorpay_status)
        if reazorpay_status == 'created':
            # if 'user_email' in request.session:
            #     user_email = request.session['user_email']
            #     user = UserDetail.objects.get(uname = user_email)
            #     try:
            #         user_ad = Address.objects.get(user=user,selected=True)
            #     except:
            #         messages.warning(request,'No address specified')
            #         return redirect('proceed_to_checkout')
            #     cart = CartItem.objects.filter(cart__user=user)
            #     try:
            #         coupon = UserCoupon.objects.get(user=user,coupon__is_active=True,applied=True)
            #         discount = coupon.coupon.discount_price
            #     except:
            #         discount = 0
            #     cartcount = cart.count()
            for c in cart:
                ord = Order(user=user, address=user_ad, product=c.product, amount=c.subtotal-(discount)/cartcount, quantity=c.quantity, order_type= 'Razorpay')
                ord.save()
                htmlgen =  f'<p>Your Celeritas Order of Order ID <strong>ORDID{ord.id}</strong> placed successfully.</p>Price: ₹ {c.subtotal-(discount)/cartcount}<p>Quantity: {c.quantity} No.s</p>'
                send_mail('Order Placed',str(ord.id),'celeritasmain2@gmail.com',[user.user_email], fail_silently=False, html_message=htmlgen)
                c.delete()
                print(Order.objects.filter(user=user))
                print("order placed razorpay")
                
            UserCoupon.objects.filter(user__user_email=user_email,coupon__is_active=True,applied=True).delete()
            return render(request,'store/confirm_order.html')
            
        else:
            messages.warning(request,'Something went wrong')
            return redirect('user_home')
    else:
        return redirect('user_login')
    
    
# @csrf_exempt
# def razorpay_callback(request):
#     if request.method == 'POST':
#         # Retrieve the POST data from Razorpay
#         razorpay_data = request.POST

#         # Verify the authenticity of the callback request
#         client = razorpay.Client(auth=("rzp_test_FzpBcunlDun1vW", "0CmJy8RJrFXmVAsInbHBJSyr"))
#         try:
#             client.utility.verify_payment_signature(razorpay_data)
#             # Signature verification successful, proceed to process the payment
#             payment_id = razorpay_data['razorpay_payment_id']
#             payment_status = razorpay_data['razorpay_event']

#             if payment_status == 'payment.authorized':
#                 # Payment is successful, mark the order as paid or update your records
#                 # You can retrieve the order ID or other necessary data from Razorpay response

#                 # Example: Update the order status
#                 # Order.objects.filter(razorpay_order_id=payment_id).update(status='paid')

#                 return JsonResponse({'status': 'success'})
#             else:
#                 # Payment failed or has another status
#                 # Handle as needed
#                 return JsonResponse({'status': 'failed'})

#         except razorpay.errors.SignatureVerificationError:
#             # Signature verification failed, possibly an invalid request
#             return JsonResponse({'status': 'error'})
#     else:
#         # Handle non-POST requests appropriately
#         return JsonResponse({'status': 'error'})