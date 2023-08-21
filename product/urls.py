from django.urls import path,include
from . import views
from .views import AdminAddProductView, AdminAddProductImageView, AddProductVariantionView, AddProductSizeView, AddProductColorView

urlpatterns = [
    path('admin_addproduct/', AdminAddProductView.as_view(), name='admin_addproduct'),
    path('add_productimage/', AdminAddProductImageView.as_view(), name='add_productimage'),
    path('add_productvariation/', AddProductVariantionView.as_view(), name='add_productvariation'),
    path('add_productsize/', AddProductSizeView.as_view(), name='add_productsize'),
    path('add_productcolor/', AddProductColorView.as_view(), name='add_productcolor'),
    
    path('', views.adminproductlist, name='admin_productlist'),
    path('admin_product_variantlist/', views.admin_product_variantlist, name='admin_product_variantlist'),
    path('admin_colorlist/', views.admin_colorlist, name='admin_colorlist'),
    path('admin_sizelist/', views.admin_sizelist, name='admin_sizelist'),
    path('admin_productgallery/', views.adminproductgallery, name='admin_productgallery'),
    path('admin_updateproduct/<int:id>/', views.updateproduct, name='admin_updateproduct'),
    path('update_size/<int:id>/', views.admin_updatesize, name='update_size'),
    path('update_color/<int:id>/', views.admin_updatecolor, name='update_color'),
    
    path('update_productvarient/<int:id>/', views.update_productvarient, name='update_productvarient'),
    path('update_productimage/<int:id>/', views.update_productimage, name='update_productimage'),
    # path('update_variantion/', UpdateVariantionView.as_view(), name='update_variantion'),
    path('delete_productvarient/', views.delete_productvarient, name='delete_productvarient'),
    path('admin_deleteproduct/', views.deleteproduct, name='admin_deleteproduct'),
    path('delete_productimage/', views.delete_productimage, name='delete_productimage'),
    path('delete_color/', views.deletecolor, name='delete_color'),
    path('delete_size/', views.deletesize, name='delete_size'),
    
    
]