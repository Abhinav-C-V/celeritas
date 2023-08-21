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


# def category_view(request):
#     categories = Category.objects.all()  # Retrieve all categories from the database
#     context = {
#         'links': categories,
#     }
#     return render(request, 'store/user_store.html', context)

class AdminAddCategoryView(View):
    def get(self, request):
        if 'username' in request.session:
            form = CategoryForm()
            return render(request, 'admin/add_category.html', {'form': form})
        else:
            return render(request, 'admin/login.html')

    def post(self, request):
        if 'username' in request.session:
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                name = form.cleaned_data['category_name']
                dup = Category.objects.filter(name=name).first()
                if dup:
                    messages.warning(request, 'Category already exists')
                    return redirect('admin_addcategory')
                else:
                    form.save()
                    return redirect('admin_categorylist')
            else:
                form = CategoryForm()
                return render(request, 'admin/add_category.html', {'form': form})
        else:
            return render(request, 'admin/login.html')

@never_cache
def admincategorylist(request):
    if 'username' in request.session:
        if 'search' in request.GET:
            search=request.GET['search']
            cat=Category.objects.filter(category_name__icontains=search)
        else:
            cat=Category.objects.all().order_by('id')
        paginator = Paginator(cat, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'admin/category_list.html',{'page_obj': page_obj})
    else:
        return render(request, 'admin/login.html')

class UpdateCategoryView(View):
    def get(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            cat = Category.objects.get(id=uid)
            form = CategoryForm(instance=cat)
            return render(request, 'admin/update_category.html', {'form': form, 'cat':cat})
        else:
            return redirect('admin_login')
    
    def post(self, request):
        if 'username' in request.session:
            uid = request.GET['uid']
            cat = Category.objects.get(id=uid)
            form = CategoryForm(request.POST, request.FILES, instance=cat)
            if form.is_valid():
                form.save()
                return redirect('admin_categorylist')
            else:
                return render(request, 'admin/update_category.html', {'form': form,'cat':cat})
        else:
            return redirect('admin_login')


def deletecategory(request):
    if 'username' in request.session:
        uid=request.GET['uid']
        Category.objects.filter(id=uid).delete()
        return redirect('admin_categorylist')
    else:
        return redirect('admin_login')