from django.urls import path,include
from . import views

urlpatterns = [
    # path('', views.store, name='store'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_wishlist_item/<int:id>/', views.remove_wishlist, name='remove_wishlist_item'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('proceed_to_checkout/', views.proceed_to_checkout, name='proceed_to_checkout'),
    path('remove_cart_item/', views.remove_cart_item, name='remove_cart_item'),
    path('decrement_cart_item/', views.decrement_cart_item, name='decrement_cart_item'),
    path('increment_cart_item/', views.increment_cart_item, name='increment_cart_item'),
    path('select_address/', views.select_address, name='select_address'),
    path('cash_on_delivery/', views.cash_on_delivery, name='cash_on_delivery'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    
    
    
    
]