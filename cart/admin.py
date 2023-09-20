from django.contrib import admin
from .models import CartItem, Cart, Wishlist, Coupon, UserCoupon, Wallet, Transaction


# Register your models here.
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(UserCoupon)
admin.site.register(Wallet)
admin.site.register(Transaction)




