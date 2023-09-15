from django.shortcuts import render, redirect
from . models import Product, ProductGallery, Variation, Size, Color
from category.models import Category

from celeritas.forms.product_form import ProductForm, ProductGalleryForm, VariationForm, ProductColorForm, ProductSizeForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import F





# Create your views here.

@never_cache
def adminproductlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search = request.GET['search']
            prod = Product.objects.filter(product_name__icontains=search)
        else:
            prod = Product.objects.all().order_by('id')

        # Add sorting by product price
        sort_by_price = request.GET.get('sort_price')
        if sort_by_price:
            if sort_by_price == 'asc':
                prod = prod.order_by('normal_price')
            elif sort_by_price == 'desc':
                prod = prod.order_by(F('normal_price').desc())

        paginator = Paginator(prod, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'admin/product_details.html', {'page_obj': page_obj})
    else:
        return render(request, 'admin/login.html')
    
@never_cache
def admin_product_variantlist(request,id):
    if 'username' in request.session:
        try:
            # prod_id = request.GET.get('prod_id')
            product = get_object_or_404(Product, id=id)
            variants = Variation.objects.filter(product=product)
        except:
            messages.warning(request,'Variants not found')
            return redirect('admin_productlist')
        paginator = Paginator(variants, 10)
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
            
        paginator = Paginator(prod, 10)
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
            prod_name = form.cleaned_data['product_name']
            normal_price = form.cleaned_data['normal_price']
            input_cat = form.cleaned_data['category']
            dup = Product.objects.filter(product_name=prod_name).first()
            if dup:
                messages.warning(request,'Product with same name already exists')
                return redirect('admin_addproduct')
            else:
                try:
                    cat = Category.objects.get(category_name = input_cat)
                except Category.DoesNotExist:
                    messages.warning(request,'No such category exists')
                    return redirect('admin_addproduct')
                print(cat.discount)
                if cat.discount:
                    if int(cat.discount) < normal_price:
                        form.save()
                        messages.success(request,'Product added successfully')
                        return redirect('admin_productlist')
                    else:
                        messages.warning(request,'Product price must be grater than discount value')
                        return redirect('admin_addproduct')
                else:
                    form.save()
                    messages.success(request,'Product added successfully')
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
            # product = form.initial.get('product')
            # color = form.initial.get('color')
            # size = form.initial.get('size')
            # Check if the same variation already exists
            # if Variation.objects.filter(product=product, color=color, size=size).exists():
                # messages.warning(request, "This variation already exists")
            
            return render(request, 'admin/add_product_variations.html', {'form': form})
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
                return redirect('add_productvariation')
                # return render(request, 'admin/add_product_variations.html', {'form': form})
            form.save()
            return redirect('admin_productlist')
        else:
            return render(request, 'admin/add_product_variations.html', {'form': form})
        
        
def admin_product_variations(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search = request.GET['search']
            prod = Variation.objects.filter(product__product_name__icontains=search)
        else:
            prod = Variation.objects.all().order_by('id')
            # Add sorting by product price
            paginator = Paginator(prod, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
        return render(request, 'admin/product_variations.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login')


class AddProductColorView(View):
    def get(self, request):
        if 'username' in request.session:
            form = ProductColorForm()
            return render(request, 'admin/add_productcolor.html', {'form': form})
        else:
            return redirect('admin_login')
           
    def post(self, request):
        if 'username' in request.session:
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
        else:
            return redirect('admin_login')
        
        
@never_cache
def admin_colorlist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            color=Color.objects.filter(color__icontains=search)
               
        else:
            color=Color.objects.all().order_by('id')
        print(color)
        paginator = Paginator(color, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/color_list.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin_login')
    
    
def admin_updatecolor(request,id):
    if 'username' in request.session:
        try:
            color = Color.objects.get(id=id)
        except Color.DoesNotExist:
            messages.warning(request, 'Selected colour does not exist')
            return redirect('admin_colorlist')
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
            size=Size.objects.filter(size__icontains=search)
               
        else:
            size=Size.objects.all().order_by('id')
        print(size)
        paginator = Paginator(size, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/size_list.html',{'page_obj': page_obj,})
    else:
        return render(request, 'admin_login')
    
    
def admin_updatesize(request,id):
    if 'username' in request.session:
        try:
            size = Size.objects.get(id=id)
        except Size.DoesNotExist:
            messages.warning(request, 'Selected Size does not exist')
            return redirect('admin_sizelist')
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
        try:
            prod = Product.objects.get(id=id)
        except Product.DoesNotExist:
            messages.warning(request, 'Selected Product does not exist')
            return redirect('admin_productlist')
        
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
        try:
            prod = Variation.objects.get(id=id)
        except Variation.DoesNotExist:
            messages.warning(request, 'Selected Variation does not exist')
            return redirect('admin_product_variantlist', id=prod.product.product.id)
        
        if request.method == 'POST':
            form = VariationForm(request.POST, request.FILES, instance=prod)
            # form = VariationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request,"Product details updated")
                return redirect('admin_product_variantlist', id=prod.product.id)
            else:
                # return render(request, 'admin/update_product_variation.html', {'form': form,'prod':prod})
                return redirect('admin_product_variantlist', id=prod.product.id)
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
        return redirect('admin_product_variations')
    else:
        return redirect('admin_login')

    
def delete_productimage(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        ProductGallery.objects.filter(id=uid).delete()
        return redirect('admin_productgallery')
    else:
        return redirect('admin_login')