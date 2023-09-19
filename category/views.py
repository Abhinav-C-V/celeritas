from django.shortcuts import render, redirect
from celeritas.forms.category_form import CategoryForm
from . models import Category
from django.contrib import messages
from django.core.paginator import Paginator
# from home_store.models import UserDetail
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


# Create your views here.



class AdminAddCategoryView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'username' in request.session:
            form = CategoryForm()
            return render(request, 'admin/add_category.html', {'form': form})
        else:
            return redirect('admin_login')
    @method_decorator(never_cache)
    def post(self, request):
        if 'username' in request.session:
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                print("form is valid")
                name = form.cleaned_data['category_name']
                discount = form.cleaned_data['discount']
                offer_active = form.cleaned_data['offer_active']
                
                dup = Category.objects.filter(category_name=name).first()
                if dup:
                    messages.warning(request, 'Category already exists')
                    return redirect('admin_addcategory')
                elif offer_active and (discount is None or discount == 0):
                    messages.warning(request, 'A discount greater than 0 is required.')
                    return redirect('admin_addcategory')
                else:
                    form.save()
                    return redirect('admin_categorylist')
            else:
                print("form is not valid")
                return redirect('admin_addcategory')
        else:
            return redirect('admin_login')

@never_cache
def admincategorylist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            cat=Category.objects.filter(category_name__icontains=search)
        else:
            cat=Category.objects.all().order_by('id')
        paginator = Paginator(cat, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/category_list.html',{'page_obj': page_obj})
    else:
        return redirect('admin_login')

class UpdateCategoryView(View):
    @method_decorator(never_cache)
    def get(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            try:
                cat = Category.objects.get(id=uid)
                form = CategoryForm(instance=cat)
            except Category.DoesNotExist:
                messages.warning(request,'Selected category does not exist')
                return redirect('admin_categorylist')
            return render(request, 'admin/update_category.html', {'form': form, 'cat':cat})
        else:
            return redirect('admin_login')
        
    @method_decorator(never_cache)
    def post(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            try:
                cat = Category.objects.get(id=uid)
            except Category.DoesNotExist:
                messages.warning(request,'Selected category does not exist')
                return redirect('admin_categorylist')
            form = CategoryForm(request.POST, request.FILES, instance=cat)
            if form.is_valid():
                form.save()
                return redirect('admin_categorylist')
            else:
                return render(request, 'admin/update_category.html', {'form': form,'cat':cat})
        else:
            return redirect('admin_login')

@never_cache
def deletecategory(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Category.objects.filter(id=uid).delete()
        return redirect('admin_categorylist')
    else:
        return redirect('admin_login')