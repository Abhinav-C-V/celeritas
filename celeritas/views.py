# from django.shortcuts import render,redirect
# from django.contrib import messages
# from django.views.generic import View
# from django.contrib.auth import authenticate, login
# from django.db.models.functions import ExtractMonth, ExtractDay
# from django.db.models import Count
# import calendar
# import io
# from celeritas.forms.category_form import CategoryForm
# from django.core.paginator import Paginator
# from home_store.models import UserDetail
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import never_cache





# class AdminLoginView(View):
#     @method_decorator(never_cache)
#     def get(self, request):
#         if 'username' in request.session:
#             return redirect('admin_dashboard')
#         else:
#             return render(request, 'admin/login.html')
        
#     @method_decorator(never_cache)
#     def post(self, request):
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             request.session['username'] = username
#             return redirect('admin_dashboard')
#         else:
#             return render(request, 'admin/login.html')
        
        
# @never_cache
# def admindashboard(request):
#     if 'username' in request.session:
#         return render(request, 'admin/index.html')
#     else:
#         return redirect('admin_login')
    
#     # if 'username' in request.session:
#     #     orders_months = Order.objects.annotate(month=ExtractMonth("ordered_date")).values('month').annotate(count=Count('id')).values('month','count')
#     #     months = []
#     #     total_ord = []
#     #     for i in orders_months:
#     #         months.append(calendar.month_name[i['month']])
#     #         total_ord.append(i['count'])
#     #         order = Order.objects.order_by('ordered_date')[:2]
#     #     return render(request, 'admindashboard.html',{'months':months,'total_ord':total_ord})
    
#     # else:
#     # return render(request, 'admin_login.html')


# @never_cache
# def admin_logout(request):
#     if 'username' in request.session:
#         del request.session['username']
#     return redirect('admin_login')

# @never_cache
# def admin_userdetails(request):
#     if 'username' in request.session:
#         if 'search' in request.GET:
#             search=request.GET['search']
#             user=UserDetail.objects.filter(user_firstname__icontains=search)
#         else:
#             user=UserDetail.objects.all().order_by('-id')
#         paginator = Paginator(user, 5)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#         return render(request,'admin/user_details.html',{'page_obj': page_obj})
#     else:
#         return render(request, 'admin/login.html')

# def admin_deleteuser(request):
#     if 'username' in request.session:
#         u_id=request.GET['uid']
#         UserDetail.objects.filter(id=u_id).delete()
#         return redirect('admin_userdetails')
#     else:
#         return redirect('admin_login')

# def admin_blockuser(request):
#     if 'username' in request.session:
#         u_id=request.GET['uid']
#         block_check=UserDetail.objects.filter(id=u_id)
#         for user in block_check:
#             if user.user_is_active:
#                 UserDetail.objects.filter(id=u_id).update(user_is_active=False)
#                 messages.warning(request, f'{user.user_firstname} is blocked')
#             else:
#                 UserDetail.objects.filter(id=u_id).update(user_is_active=True)
#                 messages.success(request, f'{user.user_firstname} is unblocked')
#         return redirect('admin_userdetails')
#     else:
#         return redirect('admin_login')
    
    
    
# def admin_bannerlist(request):
#     if 'username' in request.session:
#         if 'search' in request.GET:
#             search=request.GET['search']
#             member=Banner.objects.filter(name__icontains=search)
#         else:
#             member=Banner.objects.all().order_by('-id')
#         return render(request,'adminbannerlist.html',{'member': member})
#     else:
#         return render(request, 'adminlogin.html')
    
# def update_banner(request):
#     if 'username' in request.session:
#         uid = request.GET['uid']
#         cat = Banner.objects.get(id=uid)
#         if request.method == 'POST':
#             fm = BannerForm(request.POST, request.FILES, instance=cat)
#             if fm.is_valid():
#                 fm.save()
#                 return redirect('adminbannerlist')
#         else:
#             fm = BannerForm(instance=cat)
#             return render(request, 'adminupdatebanner.html', {'fm': fm})
#     else:
#         return redirect('adminlogin')

# def admin_addbanner(request): 
#     if 'username' in request.session:
#         if request.method == 'POST':
#             fm = BannerForm(request.POST, request.FILES)
#             if fm.is_valid():
#                 fm.save()
#                 return redirect('adminbannerlist')
#             else:
#                 return render(request, 'adminaddbanner.html', {'fm': fm})
#         else:
#             fm = BannerForm()
#             return render(request, 'adminaddbanner.html', {'fm': fm})
#     else:
#         return redirect('adminlogin')
    
# def delete_banner(request):
#     if 'username' in request.session:
#         uid=request.GET['uid']
#         Banner.objects.filter(id=uid).delete()
#         return redirect('adminbannerlist')
#     else:
#         return redirect('adminlogin')