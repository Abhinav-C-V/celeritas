from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import UserLoginView, UserSignupView, ChangePasswordView, SignupOTPView

urlpatterns = [
    # path('', views.store, name='store'),
    path('', views.index, name='user_index'),
    path('user_login', UserLoginView.as_view(), name='user_login'),
    path('user_signup', UserSignupView.as_view(), name='user_signup'),
    path('signup_otp', SignupOTPView.as_view(), name='signup_otp'),
    
    # path('edit_profile_user', EditUserView.as_view(), name='edit_profile_user'),
    path('user_logout', views.userlogout, name='user_logout'),
    path('otp_login', views.otp_login, name='otp_login'),
    path('otp_verification', views.otp_verification, name='otp_verification'),
    
    
    
    # path('forgot_password', views.forgot_password, name='forgot_password'),
    # path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    # path('reset_password', views.reset_password, name='reset_password'),
    
    path('user_home', views.userhome, name='user_home'),
    path('user_store', views.userstore_filter, name='user_store'),
    # path('userstore_filter', views.userstore_filter, name='userstore_filter'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_profile_info/', views.user_profile_info, name='user_profile_info'),
    path('edit_personal_info/', views.edit_personal_info, name='edit_personal_info'),
    path('change_password', ChangePasswordView.as_view(), name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('forgot_pass_logout_user/', views.forgot_pass_logout_user, name='forgot_pass_logout_user'),
    path('edit_email/', views.edit_email, name='edit_email'),
    path('edit_phone/', views.edit_phone, name='edit_phone'),
    path('edit_image/', views.edit_image, name='edit_image'),
    
    path('user_manage_address/', views.user_manage_address, name='user_manage_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete_address/', views.delete_address, name='delete_address'),
    
    path('orders/', views.orders, name='orders'),
    path('view_order/<int:id>/', views.view_order, name='view_order'),
    path('cancel_order/<int:id>/', views.cancel_order, name='cancel_order'),
    path('return_order/<int:id>/', views.return_order, name='return_order'),
    
    path('coupons/', views.coupons, name='coupons'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('cancel_coupon/', views.cancelcoupon, name='cancel_coupon'),
    
    path('submit_review/<int:id>/', views.submit_review, name='submit_review'),
    
    
    path('generate_invoice/', views.generate_invoice, name='generate_invoice'),
    
    
    
    
    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)