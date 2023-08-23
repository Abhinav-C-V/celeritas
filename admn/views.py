from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Count, Q, F
# from django.db.models import Q, F
import calendar
import io
from celeritas.forms.category_form import CategoryForm
from celeritas.forms.product_form import BannerForm, CouponForm, UserCouponForm, OrderForm
from django.core.paginator import Paginator
from home_store.models import UserDetail
from .models import Banner
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from cart.models import Coupon, UserCoupon, Order




class AdminLoginView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'username' in request.session:
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html')
        
    @method_decorator(never_cache)
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html')
        
        
@never_cache
def admindashboard(request):
    if 'username' in request.session:
        return render(request, 'admin/index.html')
    else:
        return redirect('admin_login')
    
    # if 'username' in request.session:
    #     orders_months = Order.objects.annotate(month=ExtractMonth("ordered_date")).values('month').annotate(count=Count('id')).values('month','count')
    #     months = []
    #     total_ord = []
    #     for i in orders_months:
    #         months.append(calendar.month_name[i['month']])
    #         total_ord.append(i['count'])
    #         order = Order.objects.order_by('ordered_date')[:2]
    #     return render(request, 'admindashboard.html',{'months':months,'total_ord':total_ord})
    
    # else:
    # return render(request, 'admin_login.html')


@never_cache
def admin_logout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('admin_login')

@never_cache
def admin_userdetails(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            user=UserDetail.objects.filter(user_firstname__icontains=search)
        else:
            user=UserDetail.objects.all().order_by('id')
        paginator = Paginator(user, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/user_details.html',{'page_obj': page_obj})
    else:
        return render(request, 'admin/login.html')

def admin_deleteuser(request):
    if 'username' in request.session:
        u_id=request.GET['uid']
        UserDetail.objects.filter(id=u_id).delete()
        return redirect('admin_userdetails')
    else:
        return redirect('admin_login')

def admin_blockuser(request):
    if 'username' in request.session:
        u_id=request.GET['uid']
        block_check=UserDetail.objects.filter(id=u_id)
        for user in block_check:
            if user.user_is_active:
                UserDetail.objects.filter(id=u_id).update(user_is_active=False)
                messages.warning(request, f'{user.user_firstname} is blocked')
            else:
                UserDetail.objects.filter(id=u_id).update(user_is_active=True)
                messages.success(request, f'{user.user_firstname} is unblocked')
        return redirect('admin_userdetails')
    else:
        return redirect('admin_login')
    
      
def admin_bannerlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            banner=Banner.objects.filter(name__icontains=search)
        else:
            banner=Banner.objects.all().order_by('id')
        paginator = Paginator(banner, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # for banner in page_obj:
        #     print(banner)
        return render(request,'admin/banner_list.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login')
        
    
def update_banner(request):
    if 'username' in request.session:
        bid = request.GET['bid']
        ban = Banner.objects.get(id=bid)
        if request.method == 'POST':
            # print(ban)
            form = BannerForm(request.POST, request.FILES, instance=ban)
            if form.is_valid():
                form.save()
                return redirect('admin_bannerlist')
        else:
            # print(ban)
            form = BannerForm(instance=ban)
            return render(request, 'admin/update_banner.html', {'form': form,'ban':ban })
    else:
        return redirect('admin_login')

class AdminAddBannerView(View):
    def get(self, request):
        if 'username' in request.session:
            form = BannerForm()
            return render(request, 'admin/add_banner.html', {'form': form})
        else:
            return redirect('admin_login')
           
    def post(self, request):
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            bann = form.cleaned_data['name'].upper()
            dup = Banner.objects.filter(name=bann).first()
            if dup:
                messages.warning(request,'Banner with same name already exists')
                return redirect('admin_addbanner')
            else:
                form.save()
                messages.success(request,'Banner added successfully')
                return redirect('admin_bannerlist')
        else:
            return render(request, 'admin/add_banner.html', {'form': form})


# def admin_addbanner(request): 
#     if 'username' in request.session:
#         if request.method == 'POST':
#             form = BannerForm(request.POST, request.FILES)
#             print(form.cleaned_data['name'])
#             if form.is_valid():
#                 form.save()
#                 print(form.cleaned_data['name'])
#                 messages.success(request,'Banner added successfully')
#                 return redirect('admin_bannerlist')
#             else:
#                 return render(request, 'admin/add_banner.html', {'form': form})
#         else:
#             form = BannerForm()
#             return render(request, 'admin/add_banner.html', {'form': form})
#     else:
#         return redirect('admin_login')

  
def delete_banner(request):
    if 'username' in request.session:
        bid=request.GET['bid']
        Banner.objects.filter(id=bid).delete()
        return redirect('admin_bannerlist')
    else:
        return redirect('admin_login')


def admin_couponlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            coupon=Coupon.objects.filter(coupon_code__icontains=search)
        else:
            coupon=Coupon.objects.all().order_by('-id')
        paginator = Paginator(coupon, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/coupon_list.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login') 
    
def add_coupon(request):
    if 'username' in request.session:     
        if request.method == 'POST':
            form = CouponForm(request.POST,request.FILES)
            if form.is_valid():
                coupon_code = form.cleaned_data['coupon_code']
                dup = Coupon.objects.filter(coupon_code=coupon_code).first()
                if dup:
                    messages.warning(request,'Coupon already exists')
                    return redirect('add_coupon')
                else: 
                    form.save()
                    messages.success(request,'Coupon added successfully')
                    return redirect('admin_couponlist')       
        else:        
            form = CouponForm()
            return render(request, 'admin/add_coupon.html',{'form':form})
    else:
        return redirect('admin_login') 

def delete_coupon(request):
    if 'username' in request.session:
        c_id=request.GET['uid']
        Coupon.objects.filter(id=c_id).delete()
        return redirect('admin_couponlist')
    else:
        return redirect('admin_login')

def update_coupon(request):
    if 'username' in request.session:
        c_id = request.GET['uid']
        coup = Coupon.objects.get(id=c_id)
        if request.method == 'POST':
            form = CouponForm(request.POST, request.FILES, instance=coup)
            if form.is_valid():
                form.save()
                messages.success(request, 'Coupon updated successfully')
                return redirect('admin_couponlist')
        else:
            form = CouponForm(instance=coup)
            return render(request, 'admin/update_coupon.html', {'form': form,'coup':coup })
    else:
        return redirect('admin_login')
    
    
    
def admin_user_couponlist(request):
    if 'username' in request.session:
        # uid=request.GET['uid']
        if 'search' in request.GET:
            search=request.GET['search']
            # print(uid)
            coupon=UserCoupon.objects.filter(coupon__coupon_code__icontains=search )
        else:
            uid=request.GET['uid']
            coupon=UserCoupon.objects.filter(user=uid).order_by('id')
        paginator = Paginator(coupon, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/user_couponlist.html',{'page_obj': page_obj,})
    else:
        return redirect('admin_login') 
    
def add_user_coupon(request):
    if 'username' in request.session:     
        if request.method == 'POST':
            form = UserCouponForm(request.POST,request.FILES)
            if form.is_valid():
                coupon = form.cleaned_data['coupon']
                user = form.cleaned_data['user']
                print(coupon)
                dup = UserCoupon.objects.filter(coupon=coupon,user=user).first()
                if dup:
                    messages.warning(request,'User Coupon already exists')
                    return redirect('add_user_coupon')
                else: 
                    form.save()
                    messages.success(request,'User Coupon added successfully')
                    return redirect('admin_userdetails')       
        else:        
            form = UserCouponForm()
            return render(request, 'admin/add_usercoupon.html',{'form':form})
    else:
        return redirect('admin_login') 

def delete_user_coupon(request):
    if 'username' in request.session:
        c_id=request.GET['uid']
        UserCoupon.objects.filter(id=c_id).delete()
        return redirect('admin_userdetails')
    else:
        return redirect('admin_login')
    
    
def admin_orderlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            member=Order.objects.filter(Q(user__user_firstname__icontains=search)|Q(id__icontains=search)).order_by('-id')
        else:
            member = Order.objects.all().order_by('-id')
        paginator = Paginator(member, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/order_list.html', {'page_obj': page_obj})
    else:
        return render('admin_login')
    
class OrderUpdateView(View):
    def get(self, request, id):
        if 'username' in request.session:
            ord = Order.objects.get(id=id)
            form = OrderForm(instance=ord)
            return render(request, 'admin/update_orders.html', {'form': form,'ord':ord})
        else:
            return redirect('admin_login')

    def post(self, request, id):
        if 'username' in request.session:
            ord = Order.objects.get(id=id)
            form = OrderForm(request.POST, request.FILES, instance=ord)
            if form.is_valid():
                form.save()
                messages.success(request,'Order updated successfully')
                return redirect('admin_orderlist')
            else:
                return render(request, 'admin/update_orders.html', {'form': form,'ord':ord})
        else:
            return redirect('admin_login')


