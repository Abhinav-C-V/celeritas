from django.urls import path,include
from . import views
from .views import  UpdateCategoryView, AdminAddCategoryView

urlpatterns = [
    # path('', views.store, name='store'),
    path('add_category/', AdminAddCategoryView.as_view(), name='admin_addcategory'),
    path('update_category/', UpdateCategoryView.as_view(), name='admin_updatecategory'),
    path('delete_category/', views.deletecategory, name='admin_deletecategory'),
    path('', views.admincategorylist, name='admin_categorylist'),
    
    
    
]