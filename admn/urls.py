# from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from . views import AdminLoginView, OrderUpdateView

urlpatterns = [
    
    path('', AdminLoginView.as_view(), name='admin_login'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_dashboard/', views.admindashboard, name='admin_dashboard'),
    path('admin_userdetails/', views.admin_userdetails, name='admin_userdetails'),
    path('admin_blockuser/', views.admin_blockuser, name='admin_blockuser'),
    path('admin_deleteuser/', views.admin_deleteuser, name='admin_deleteuser'),
    
    path('update_banner/', views.update_banner, name='update_banner'),
    path('admin_addbanner/', views.admin_addbanner, name='admin_addbanner'),
    path('admin_bannerlist/', views.admin_bannerlist, name='admin_bannerlist'),
    path('delete_banner/', views.delete_banner, name='delete_banner'),
    
    path('admin_couponlist/', views.admin_couponlist, name='admin_couponlist'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('update_coupon/', views.update_coupon, name='update_coupon'),
    path('delete_coupon/', views.delete_coupon, name='delete_coupon'),
    
    path('admin_user_couponlist/', views.admin_user_couponlist, name='admin_user_couponlist'),
    path('add_user_coupon/', views.add_user_coupon, name='add_user_coupon'),
    path('delete_user_coupon/', views.delete_user_coupon, name='delete_user_coupon'),
    
    path('admin_orderlist/', views.admin_orderlist, name='admin_orderlist'),
    path('admin_updateorder/<int:id>/', OrderUpdateView.as_view(), name='admin_updateorder'),
    
    
    
    
    
    
    

      
    # path('store/', include('store.urls'))
]
