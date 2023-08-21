from django.shortcuts import render, redirect
from . models import Product, ProductGallery, Variation, Size, Color

from celeritas.forms.product_form import ProductForm, ProductGalleryForm, VariationForm, ProductColorForm, ProductSizeForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache





# Create your views here.

@never_cache
def adminproductlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            prod=Product.objects.filter(product_name__icontains=search)
        else:
            prod=Product.objects.all().order_by('id')
        paginator = Paginator(prod, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/product_details.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin/login.html')
    
@never_cache
def admin_product_variantlist(request):
    if 'username' in request.session:
        try:
            prod_id = request.GET.get('prod_id')
            product = get_object_or_404(Product, id=prod_id)
            variants = Variation.objects.filter(product=product)
        except:
            messages.warning(request,'Variants not found')
            return redirect('admin_productlist')
        paginator = Paginator(variants, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'admin/product_variantlist.html', {'page_obj': page_obj})
    else:
        return render(request, 'admin/login.html')


@never_cache
def adminproductgallery(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            prod=ProductGallery.objects.filter(product__product__product_name__icontains=search)
        else:
            prod=ProductGallery.objects.all().order_by('id')
            
        paginator = Paginator(prod, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/product_gallery.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin/login.html')

class AdminAddProductView(View):
    def get(self, request):
        if 'username' in request.session:
            form = ProductForm()
            return render(request, 'admin/add_product.html', {'form': form})
        else:
            return redirect('admin_login')
           
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_productlist')
        else:
            return render(request, 'admin/add_product.html', {'form': form})


class AdminAddProductImageView(View):
    def get(self, request):
        if 'username' in request.session:
            form = ProductGalleryForm()
            return render(request, 'admin/add_image_for_product.html', {'form': form})
        else:
            return redirect('admin_login')
    
    def post(self, request):
        form = ProductGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_productgallery')
        else:
            return render(request, 'admin/add_image_for_product.html', {'form': form})
        
        
class AddProductVariantionView(View):
    def get(self, request):
        if 'username' in request.session:
            form = VariationForm()
            # Get the product, color, and size values from the form's initial data
            product = form.initial.get('product')
            color = form.initial.get('color')
            size = form.initial.get('size')
            # Check if the same variation already exists
            if Variation.objects.filter(product=product, color=color, size=size).exists():
                messages.warning(request, "This variation already exists")
            
            return render(request, 'admin/product_variations.html', {'form': form})
        else:
            return redirect('admin_login')

    def post(self, request):
        form = VariationForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.cleaned_data.get('product')
            color = form.cleaned_data.get('color')
            size = form.cleaned_data.get('size')
            # Check if the same variation already exists
            if Variation.objects.filter(product=product, color=color, size=size).exists():
                # form.add_error(None, 'This variation already exists.')
                messages.warning(request, "This variation already exists")
                return render(request, 'admin/product_variations.html', {'form': form})
            form.save()
            return redirect('admin_productlist')
        else:
            return render(request, 'admin/product_variations.html', {'form': form})


class AddProductColorView(View):
    def get(self, request):
        if 'username' in request.session:
            form = ProductColorForm()
            return render(request, 'admin/add_productcolor.html', {'form': form})
        else:
            return redirect('admin_login')
           
    def post(self, request):
        form = ProductColorForm(request.POST, request.FILES)
        if form.is_valid():
            color = form.cleaned_data['color'].upper()
            dup = Color.objects.filter(color=color).first()
            if dup:
                messages.warning(request,'Colour already exists')
                return redirect('add_productcolor')
            else: 
                form.save()
                messages.success(request,'Colour added successfully')
                return redirect('admin_colorlist')
        else:
            return render(request, 'admin/add_productcolor.html', {'form': form})
        
        
@never_cache
def admin_colorlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            color=Color.objects.filter(product_name__icontains=search)
               
        else:
            color=Color.objects.all().order_by('id')
        print(color)
        paginator = Paginator(color, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/color_list.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin_login')
    
    
def admin_updatecolor(request,id):
    if 'username' in request.session:
        color = Color.objects.get(id=id)
        if request.method == 'POST':
            form = ProductColorForm(request.POST, request.FILES, instance=color)
            if form.is_valid():
                form.save()
                messages.success(request,"Color details updated")
                return redirect('admin_colorlist')
            else:
                return render(request, 'admin/update_color.html', {'form': form,'color':color})
        else:
            form = ProductColorForm(instance=color)
            return render(request, 'admin/update_color.html', {'form': form,'color':color})
    else:
        return redirect('admin_login')
    
def deletecolor(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Color.objects.filter(id=uid).delete()
        return redirect('admin_colorlist')
    else:
        return redirect('admin_login')
    
    
        
class AddProductSizeView(View):
    def get(self, request):
        if 'username' in request.session:
            form = ProductSizeForm()
            return render(request, 'admin/add_productsize.html', {'form': form})
        else:
            return redirect('admin_login')
           
    def post(self, request):
        form = ProductSizeForm(request.POST, request.FILES)
        if form.is_valid():
            size = form.cleaned_data['size']
            dup = Size.objects.filter(size=size).first()
            if dup:
                messages.warning(request,'Size already exists')
                return redirect('add_productsize')
            else: 
                form.save()
                messages.success(request,'Size added successfully')
                return redirect('admin_sizelist')
        else:
            return render(request, 'admin/add_productsize.html', {'form': form})
        
@never_cache
def admin_sizelist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            size=Size.objects.filter(product_name__icontains=search)
               
        else:
            size=Size.objects.all().order_by('id')
        print(size)
        paginator = Paginator(size, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/size_list.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin_login')
    
    
def admin_updatesize(request,id):
    if 'username' in request.session:
        size = Size.objects.get(id=id)
        if request.method == 'POST':
            form = ProductSizeForm(request.POST, request.FILES, instance=size)
            if form.is_valid():
                form.save()
                messages.success(request,"Size details updated")
                return redirect('admin_sizelist')
            else:
                return render(request, 'admin/update_size.html', {'form': form,'size':size})
        else:
            form = ProductSizeForm(instance=size)
            return render(request, 'admin/update_size.html', {'form': form,'size':size})
    else:
        return redirect('admin_login')
    
def deletesize(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Size.objects.filter(id=uid).delete()
        return redirect('admin_sizelist')
    else:
        return redirect('admin_login')


def updateproduct(request,id):
    if 'username' in request.session:
        prod = Product.objects.get(id=id)
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=prod)
            if form.is_valid():
                form.save()
                messages.success(request,"Product details updated")
                return redirect('admin_productlist')
            else:
                return render(request, 'admin/update_product.html', {'form': form,'prod':prod})
        else:
            form = ProductForm(instance=prod)
            return render(request, 'admin/update_product.html', {'form': form,'prod':prod})
    else:
        return redirect('admin_login')
    
    
def update_productvarient(request,id):
    if 'username' in request.session:
        prod = Variation.objects.get(id=id)
        if request.method == 'POST':
            form = VariationForm(request.POST, request.FILES, instance=prod)
            # form = VariationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request,"Product details updated")
                return redirect('admin_productlist')
            else:
                return render(request, 'admin/update_product_variation.html', {'form': form,'prod':prod})
        else:
            form = VariationForm(instance=prod)
            return render(request, 'admin/update_product_variation.html', {'form': form,'prod':prod})
    else:
        return redirect('admin_login')
    
    
def update_productimage(request,id):
    if 'username' in request.session:
        prod = ProductGallery.objects.get(id=id)
        if request.method == 'POST':
            form = ProductGalleryForm(request.POST, request.FILES, instance=prod)
            if form.is_valid():
                form.save()
                messages.success(request,"Product image updated")
                return redirect('admin_productgallery')
            else:
                return render(request, 'admin/update_image_for_product.html', {'form': form,'prod':prod})
        else:
            form = ProductGalleryForm(instance=prod)
            return render(request, 'admin/update_image_for_product.html', {'form': form,'prod':prod})
    else:
        return redirect('admin_login')
    


    
def deleteproduct(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Product.objects.filter(id=uid).delete()
        return redirect('admin_productlist')
    else:
        return redirect('admin_login')


def delete_productvarient(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Variation.objects.filter(id=uid).delete()
        return redirect('user_manage_address')
    else:
        return redirect('admin_login')

    
def delete_productimage(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        ProductGallery.objects.filter(id=uid).delete()
        return redirect('admin_productgallery')
    else:
        return redirect('admin_login')