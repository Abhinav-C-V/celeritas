from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.db.models.functions import ExtractMonth, ExtractDay
from django.db.models import Count, Q, F
# from django.db.models import Q, F
import calendar
import io
# from celeritas.forms.category_form import CategoryForm
from celeritas.forms.product_form import BannerForm, CouponForm, UserCouponForm, OrderForm
from django.core.paginator import Paginator
from home_store.models import UserDetail
from .models import Banner
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from cart.models import Coupon, UserCoupon, Order

from django.db.models import Sum
from datetime import datetime, timedelta

from django.http import HttpResponse, FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import pandas as pd
import openpyxl
from cart.models import Order 

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet





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
        # Calculate the start and end dates for the last month
        today = datetime.today()
        last_month_end = today - timedelta(days=1)
        last_month_start = last_month_end - timedelta(days=29)
        
        total_users = UserDetail.objects.all().count()

        last_month_orders = Order.objects.filter(ordered_date__gte=last_month_start,ordered_date__lte=last_month_end,status='Delivered')
        
        last_month_completed_orders = last_month_orders.count()
        last_month_expected_orders = int(total_users * 2)
        last_month_incomplete_orders = Order.objects.filter(ordered_date__gte=last_month_start,ordered_date__lte=last_month_end,).exclude(status='Delivered').count()
        
        last_month_revenue = last_month_orders.aggregate(total_revenue=Sum('amount'))['total_revenue']
        if last_month_revenue is None:
            last_month_revenue = 0
        last_month_expected_revenue = int(total_users * 2000)
        
        
        
        context = {
            'orders': last_month_completed_orders,
            'incomplete_orders': last_month_incomplete_orders,
            'expected_orders':last_month_expected_orders,
            
            'expected_revenue': last_month_expected_revenue,
            'revenue': last_month_revenue,
            
            'users': total_users,
            
        }
        return render(request, 'admin/index.html', context)
    else:
        return redirect('admin_login')
    

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
            print(user)
        paginator = Paginator(user, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/user_details.html',{'page_obj': page_obj})
    else:
        return render(request, 'admin/login.html')

@never_cache
def admin_deleteuser(request):
    if 'username' in request.session:
        u_id=request.GET['uid']
        UserDetail.objects.filter(id=u_id).delete()
        return redirect('admin_userdetails')
    else:
        return redirect('admin_login')

@never_cache
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
    
@never_cache    
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
        return render(request,'admin/banner_list.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login')
        
@never_cache
def update_banner(request):
    if 'username' in request.session:
        bid = request.GET['bid']
        try:
            ban = Banner.objects.get(id=bid)
        except Banner.DoesNotExist:
            messages.warning(request,'Selected banner not found')
            return redirect('admin_bannerlist')
        if request.method == 'POST':
            form = BannerForm(request.POST, request.FILES, instance=ban)
            if form.is_valid():
                form.save()
                return redirect('admin_bannerlist')
        else:
            form = BannerForm(instance=ban)
            return render(request, 'admin/update_banner.html', {'form': form,'ban':ban })
    else:
        return redirect('admin_login')

class AdminAddBannerView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'username' in request.session:
            form = BannerForm()
            return render(request, 'admin/add_banner.html', {'form': form})
        else:
            return redirect('admin_login')
           
    @method_decorator(never_cache)
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

@never_cache
def delete_banner(request):
    if 'username' in request.session:
        bid=request.GET['bid']
        Banner.objects.filter(id=bid).delete()
        return redirect('admin_bannerlist')
    else:
        return redirect('admin_login')

@never_cache
def admin_couponlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            coupon=Coupon.objects.filter(coupon_code__icontains=search)
        else:
            coupon=Coupon.objects.all().order_by('-id')
        paginator = Paginator(coupon, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/coupon_list.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login') 

@never_cache
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

@never_cache
def delete_coupon(request):
    if 'username' in request.session:
        c_id=request.GET['uid']
        Coupon.objects.filter(id=c_id).delete()
        return redirect('admin_couponlist')
    else:
        return redirect('admin_login')

@never_cache
def update_coupon(request):
    if 'username' in request.session:
        try:
            c_id = request.GET['uid']
            coup = Coupon.objects.get(id=c_id)
        except Coupon.DoesNotExist:
            messages.warning(request,'Selected Coupon does not exist.')
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
    
    
@never_cache
def admin_user_couponlist(request):
    if 'username' in request.session:
        # uid=request.GET['uid']
        if 'search' in request.GET:
            search=request.GET['search']
            # print(uid)
            coupon=UserCoupon.objects.filter(coupon__coupon_code__icontains=search)
        else:
            uid=request.GET['uid']
            coupon=UserCoupon.objects.filter(user=uid).order_by('id')
        paginator = Paginator(coupon, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/user_couponlist.html',{'page_obj': page_obj,})
    else:
        return redirect('admin_login') 

@never_cache
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

@never_cache
def delete_user_coupon(request):
    if 'username' in request.session:
        c_id=request.GET['uid']
        UserCoupon.objects.filter(id=c_id).delete()
        return redirect('admin_userdetails')
    else:
        return redirect('admin_login')
    

@never_cache
def admin_orderlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            order=Order.objects.filter(Q(user__user_firstname__icontains=search)|Q(id__icontains=search)).order_by('-id')
        else:
            order = Order.objects.all().order_by('-id')
        paginator = Paginator(order, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/order_list.html', {'page_obj': page_obj})
    else:
        return render('admin_login')
    
class OrderUpdateView(View):
    def get(self, request, id):
        if 'username' in request.session:
            try:
                ord = Order.objects.get(id=id)
                form = OrderForm(instance=ord)
            except Order.DoesNotExist:
                messages.warning(request,'Selected order does not exist')
                return redirect('admin_orderlist')
                
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


def generate_pdf_report(orders, start_date, end_date):
    # Create a buffer to receive PDF data.
    buffer = BytesIO()
    
    # Use landscape orientation to make the PDF fit better.
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    
    # Container for the PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    
    # Add a heading
    elements.append(Paragraph("Sales Report", style_heading))
    elements.append(Spacer(1, 12))
    
    # Convert dates to formatted strings
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    
    # Add date range to the report
    date_range = f"Date Range: {start_date} to {end_date}"
    elements.append(Paragraph(date_range, style_normal))
    elements.append(Spacer(1, 12))
    
    # Create a data table
    table_data = [['Customer Name', 'Product Title', 'Order Date and Time', 'Order Status', 'Payment Status']]
    
    for order in orders:
        row = [order.address.user, order.product.product.product_name, order.ordered_date.strftime("%Y-%m-%d %H:%M:%S"), order.status, order.order_type]
        table_data.append(row)
    
    # Create the table and style it
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    # Build the PDF document
    doc.build(elements)
    
    # Rewind the buffer and return the PDF file
    buffer.seek(0)
    return buffer



@never_cache
def sales_report(request):
    if 'username' in request.session:
        if request.method == 'POST':
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            generate = request.POST.get('generate')
            
            # Convert today's date to a datetime.date object
            today_date = datetime.now().date()
            
            # Check if start_date and end_date are provided and in the correct format
            if not start_date_str or not end_date_str:
                messages.warning(request, 'Check dates')
                return redirect('sales_report')
            
            # Convert start_date and end_date strings to datetime.date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Check the date range
            if end_date < start_date:
                messages.warning(request, 'End date is less than start date')
                return redirect('sales_report')
            elif end_date > today_date:
                messages.warning(request, 'End date is greater than today\'s date')
                return redirect('sales_report')
            
            # Fetch orders based on the date range
            orders = Order.objects.filter(ordered_date__range=[start_date, end_date]).order_by('-ordered_date')
            
            if not orders.exists():
                messages.warning(request, 'No data found')
                return redirect('sales_report')
            
            if generate == 'PDF':
                pdf_buffer = generate_pdf_report(orders, start_date, end_date)
                return FileResponse(pdf_buffer, as_attachment=True, filename="SalesReport.pdf")
            else:
                # Generate Excel or other formats as needed
                orders = Order.objects.filter(ordered_date__range=[start_date, end_date])
                if not orders.exists():
                    messages.warning(request,'No data found')
                    return redirect('sales_report') 
                orders_df = pd.DataFrame(list(orders.values()))
                try:
                    orders_df.drop(['user_id', 'address_id'], axis=1, inplace=True)
                except:
                    messages.warning(request,'Something wrong')
                    return redirect('sales_report')
                orders_df.rename(columns={'product_id': 'product_id', 'amount': 'amount', 'ordered_date': 'ordered_date', 'order_type': 'order_type', 'status': 'status'}, inplace=True)
                orders_df['ordered_date'] = orders_df['ordered_date'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
                orders_df.to_excel(response, index=False)
                return response
        else:
            return redirect('admin_dashboard')
    else:
        return redirect('admin_login')
