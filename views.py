from django.forms.forms import BaseForm
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect, Http404, StreamingHttpResponse, FileResponse, HttpResponseForbidden
from .models import Bb, Rubric, Comment, Img  
from django.template import loader
from .forms import BbForm, RegisterUserForm, RubricFormSet, SearchForm, ImgForm, ImgNonModel
from django.forms import modelformset_factory, inlineformset_factory
from django.forms.formsets import ORDERING_FIELD_NAME
from django.urls import reverse_lazy, reverse
from django.template.loader import get_template, render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.gzip import gzip_page
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView, DeleteView, CreateView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, DayArchiveView, DateDetailView
from django.views.generic.detail import SingleObjectMixin
from django.core.paginator import Paginator
from django.forms.models import BaseModelFormSet
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from precise_bbcode.bbcode import get_parser

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.forms import formset_factory

from samplesite.settings import BASE_DIR
from datetime import datetime
import os

from django.contrib.auth.password_validation import UserAttributeSimilarityValidator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import sign_data, unsign_data
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.signing import Signer

def my_view(request):
    messages.success(request, 'Данные успешно отправлены!')

    signer = Signer()
    signed_value = signer.sign('some_data')
    print(f"Подписанные данные: {signed_value}")
    try:
        original_value = signer.unsign(signed_value)
        print(f"Оригинальные данные: {original_value}")
    except:
        print("Ошибка при расшифровке")


    return redirect(reverse('bboard:success_view'))



def success_view(request):
    return render(request, 'success.html')


def button_view(request):
    if request.method == 'POST':
        return redirect('/bboard/button/?message=success')
    return render(request, 'button.html')




def get_comments(request):
    comments = Comment.objects.all().values('id', 'text', 'created_at')
    return JsonResponse(list(comments), safe=False)

def get_comment_by_id(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    return JsonResponse({'id': comment.id, 'text': comment.text, 'created_at': comment.created_at})

def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return JsonResponse({'status': 'success'})
    except Comment.DoesNotExist:
        return HttpResponseNotFound({'status': 'comment not found'})


class UserCreate(CreateView, LoginRequiredMixin):
    template_name = 'bboard/createuser.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('bboard:index')

class BbCreateView(SuccessMessageMixin, CreateView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    # success_url = reverse_lazy('bboard:index')
    success_url = 'bboard/{rubric_id}'
    success_message = 'Оъбъявление о продаже товара "%(title)s" создано'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context

def redirect_to_index(request):
    return HttpResponseRedirect(reverse('bboard:index'))


# @login_required(login_url='/login/')
# @user_passes_test(lambda user: user.is_superuser)
# @permisions_required('bboard:view_rubric')
def index(request):
    rubrics = Rubric.objects.all()
    bbs = Bb.objects.all()
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    url1 = reverse('bboard:index')
    # print(request.headers['Content-Language'])
    context = {'bbs': page.object_list, 'rubrics': rubrics, 'url1': url1, 'page': page}
    return render(request, 'bboard/index.html', context)

    # date = {'title': 'Мотоцикл', 'content': 'Старый', 'price': 10000.0}
    # return JsonResponse(date, json_dumps_params={'ensure_ascii': False})


def by_rubric(request, rubric_id):
    bbs = Bb.objects.filter(rubric=rubric_id)
    rubrics = Rubric.objects.all()
    current_rubric = Rubric.objects.get(pk=rubric_id)
    url = reverse('bboard:by_rubric', args=(current_rubric.pk,))

    context = {'bbs': bbs, 'rubrics': rubrics, 'current_rubric': current_rubric, 'url': url}
    return render(request, 'bboard/by_rubric.html', context)

def redirect_to_rubric(request, rubric_id):
    return redirect('bboard:by_rubric', rubric_id=rubric_id)


@require_http_methods(['GET', 'POST'])
def add_and_save(request):
    if request.method == 'POST':
        bbf = BbForm(request.POST)
        if bbf.is_valid():
            bbf.save()
            return HttpResponseRedirect(reverse('bboard:by_rubric', kwargs={'rubric_id': bbf.cleaned_data['rubric'].pk}))
        else:
            context = {'form': bbf}
            return render(request, 'bboard/create.html', context)
    else:
        bbf = BbForm
        context = {'form': bbf}
        return render(request, 'bboard/create.html', context)
    

# def detail(request, pk):
# # def detail(request, bb_id):
#     parser = get_parser()
#     # bb = get_list_or_404(Bb, pk=bb_id)
#     bb = Bb.objects.get(pk=pk)
#     parsed_content = parser.render(bb.content)
#     return HttpResponse(f'Название: {bb.title}, Описание: {bb.content}, Дата публикации: {bb.published}')


def detail(request, pk):
    parser = get_parser()
    bb = Bb.objects.get(pk=pk)
    parsed_content = parser.render(bb.content)
    
    context = {
        'bb': bb,
        'parsed_content': parsed_content,
    }
    return render(request, 'bboard/detail.html', context)

class BbDetailView(DetailView):
    model = Bb

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rubric'] = Rubric.objects.all()
        return context


class BbAddView(FormView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    initial = {'price': 0.0}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        self.object = super().get_form(form_class)
        return self.object
    
    def get_success_url(self):
        return reverse('bboard:by_rubric', kwargs={'rubric_id': self.object.cleaned_data['rubric'].pk})
    


class BbEditView(UpdateView):
    model = Bb
    form_class = BbForm
    success_url = '/'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context
    

class BbDeleteView(DeleteView):
    model = Bb
    success_url = '/'

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


class BbIndexView(ArchiveIndexView):
    model = Bb
    date_field = 'published'
    date_list_period = 'year'
    template_name = 'bboard/index.html'
    context_object_name = 'bbs'
    allow_empty = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        context['url1'] = reverse_lazy('bboard:index')
        return context
    

class BbMonthArchiveView(DayArchiveView):
    model = Bb
    date_field = 'published'
    month_format = '%m'
    template_name = 'bboard/bb_archive_month.html'


class BbRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Используем reverse для получения правильного URL-адреса
        return reverse('bboard:detail', kwargs={'pk': self.kwargs['pk']})
    




class BbByRubricView(SingleObjectMixin ,ListView):
    template_name = 'bboard/by_rubric.html'
    pk_url_kwarg = 'rubric_id'   


    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Rubric.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_rubric'] = self.object
        context['rubrics'] = Rubric.objects.all()
        context['bbs'] = context['object_list']
        context['ulist'] = ['PHP', ['Python', 'Django'], ['JavaScript', 'Node.js', 'Express']]
        return context
    
    def get_queryset(self):
        return self.object.bb_set.all()
    


def edit(request, pk):
    bb = Bb.objects.get(pk=pk)
    if request.method == 'POST':
        bbf = BbForm(request.POST, instance=bb)
        if bbf.is_valid():
            bbf.save()

            messages.success(request, 'Объявление исправлено')  
            storage = messages.get_messages(request)  
            first_message_text = list(storage)[0].message 
            print(first_message_text) 

            return HttpResponseRedirect(reverse('bboard:by_rubric', kwargs={'rubric_id': bbf.cleaned_data['rubric'].pk}))
        else:
            context = {'form': bbf}
            return render(request, 'bboard/bb_form.html', context)
    else:
        bbf = BbForm(instance=bb)
        context = {'form': bbf}
        return render(request, 'bboard/bb_form.html', context)
    


# def rubric_view(request):

#     RubricFormSet = modelformset_factory(Rubric, fields=('name',), can_order=True, can_delete=True)

#     if request.method == 'POST':
#         formset = RubricFormSet(request.POST)
#         # if formset.is_valid():
#         #     formset.save()
#         #     return redirect('bboard:index') 
#         formset.save(commit=False)  # Сохранить без коммита
#         for rubric in formset.deleted_objects:
#             rubric.delete()  # Удалить объекты
#         formset.save()  # Теперь сохранить изменения
#         return redirect('bboard:index')
#     else:
#         formset = RubricFormSet()

#     return render(request, 'bboard/form.html', {'formset': formset})


# class RubricBaseForm(BaseModelFormSet):
#     def clean(self):
#         super().clean()
#         names = [form.cleaned_data['name'] for form in self.forms if 'name' in form.cleaned_data]
#         if ('Недвижимость' not in names) or ('Транспорт' not in names) or ('Еда' not in names):
#             raise ValidationError('Добавьте рубрики недвижимости, транспорта и мебели')




# def rubric_view(request):
#     RubricFormSet = modelformset_factory(Rubric, fields=('name',), can_order=True, can_delete=True, formset=RubricBaseForm)
#
#     if request.method == 'POST':
#         formset = RubricFormSet(request.POST, queryset=Rubric.objects.all())
#         if formset.is_valid():
#             for form in formset:
#                 if form.cleaned_data and form not in formset.deleted_forms:
#                     rubric = form.save(commit=False)
#                     rubric.order = form.cleaned_data[ORDERING_FIELD_NAME]
#                     rubric.save()
#             for form in formset.deleted_forms:
#                 if form.cleaned_data:
#                     form.instance.delete()
#             return redirect('bboard:index')
#     else:
#         formset = RubricFormSet(queryset=Rubric.objects.all())
#
#     return render(request, 'bboard/form.html', {'formset': formset})



def bbs(request, rubric_id):
    BbsFormSet = inlineformset_factory(Rubric, Bb, form=BbForm, extra=1)
    rubric = Rubric.objects.get(pk=rubric_id)
    if request.method == 'POST':
        formset = BbsFormSet(request.POST, instance=rubric)
        if formset.is_valid():
            formset.save()
            return redirect('bboard:index')
    else:
        formset = BbsFormSet(instance=rubric)

    return render(request, 'bboard/bbs.html', {'formset': formset, 'current_rubric': rubric})


def search(request):
    if request.method == 'POST':
        sf = SearchForm(request.POST)
        if sf.is_valid():
            keyword = sf.cleaned_data['keyword']
            rubric_id = sf.cleaned_data['rubric'].pk
            bbs = Bb.objects.filter(title__icontains=keyword, rubric_id=rubric_id) 
            context = {'bbs': bbs}
            return render(request, 'bboard/search_results.html', context)
    else:
        sf = SearchForm()
    
    context = {'form': sf}
    return render(request, 'bboard/search.html', context)



def formset_processing(request):
    FS = formset_factory(SearchForm, extra=3, can_order=True, can_delete=True)

    if request.method == 'POST':
        formset = FS(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data['DELETE']:
                    keyword = form.cleaned_data['keyword']
                    rubric_id = form.cleaned_data['rubric'].pk
                    order = form.cleaned_data['ORDER']
            return render(request, 'bboard/process_result.html')
    else:
        formset = FS(auto_id=False)
    context = {'formset': formset}
    return render(request, 'bboard/process_formset.html', context)


# def add(request):
#     if request.method == 'POST':
#         form = ImgForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('bboard:index')
#     else:
#         form = ImgForm()
#     context = {'form': form}
#     return render(request, 'bboard/add.html', context)


def addNonModelForm(request):
    if request.method == 'POST':
        form = ImgNonModel(request.POST, request.FILES)
        if form.is_valid():
            desc = form.cleaned_data['desc']
            for img_file in request.FILES.getlist('imgs'):
                img_instance = Img(img=img_file, desc=desc)
                img_instance.save()
            return redirect('bboard:index')
    else:
        form = ImgNonModel()
    context = {'form': form}
    return render(request, 'bboard/addNon.html', context)


def image_list(request):
    images = Img.objects.all()
    return render(request, 'bboard/image_list.html', {'images': images})


def delete_image(request, img_id):
    if request.method == 'POST':
        img = get_object_or_404(Img, pk=img_id)
        img.delete()
        return redirect('bboard:image_list')
    return HttpResponseForbidden("Неверный метод запроса.")



FILES_ROOT = os.path.join(BASE_DIR, 'files')

def add(request):
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['img']

            fn = '%s%s' % (datetime.now().timestamp(), os.path.splitext(uploaded_file.name)[1])
            fn = os.path.join(FILES_ROOT, fn)
            

            if not os.path.exists(FILES_ROOT):
                os.makedirs(FILES_ROOT)
            

            with open(fn, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            return redirect('bboard:index')
    else:
        form = ImgForm()
    
    context = {'form': form}
    return render(request, 'bboard/add.html', context)







# def index2(request):
#     imgs = []
#     for entry in os.scandir(FILES_ROOT):
#         imgs.append(os.path.basename(entry))
#     context = {'imgs': imgs}
#     return render(request, 'bboard/index2.html', context)


def index2(request):
    return render(request, 'bboard/index2.html')

def get(request, filename):
    fn = os.path.join(FILES_ROOT, filename)
    return FileResponse(open(fn, 'rb'), content_type='application/octet-stream')



# def my_login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)


# def my_logout(request):
#     logout(request)


# class NoForbiddenCharsValidator:
#     def __init__(self, forbidden_chars=(' ',)):
#         self.forbidden_chars = forbidden_chars

#     def validate(self, password, user=None):
#         for fc in self.forbidden_chars:
#             if fc in password:
#                 raise ValidationError(
#                     'Пароль не должен содержать недопустимые ' + \
#                      'символы %s' % ', '.join(self.forbidden_chars),
#                      code='forbidden_chars_present'
#                 )
    
#     def get_help_text(self):
#         return 'Пароль не должен содержать символы %s' % ', '.join(self.forbidden_chars)