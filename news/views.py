from datetime import datetime
from django.core.cache import cache
from locale import format_string

from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post, UserSubscribers, PostCategory, Category
from .filters import PostFilter
from .forms import PostForm
from .tasks import send_mail_new_post
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
import logging


def log(request):
    logger1 = logging.getLogger("django")
    logger1.error("Test_dj_error")
    logger1.debug('Test_dj_debug')
    logger1.info('Test_dj_info')
    logger1.critical('Test_dj_critical')
    logger1.warning('Test_dj_warning')

    logger2 = logging.getLogger('django.request')
    logger2.debug('Test_dj_RQ_debug')
    logger2.info('Test_dj_RQ_info')
    logger2.critical('Test_dj_RQ_critical')
    logger2.warning('Test_dj_RQ_warning')
    logger2.error("Test_dj_rq_error")

    logger3 = logging.getLogger('django.server')
    logger3.debug('Test_dj_SERVER_debug')
    logger3.info('Test_dj_SERVER_info')
    logger3.critical('Test_dj_SERVER_critical')
    logger3.warning('Test_dj_SERVER_warning')
    logger3.error("Test_dj_SERVER_error")

    logger4 = logging.getLogger('django.template')
    logger4.debug('Test_dj_TEMLATE_debug')
    logger4.info('Test_dj_TEMLATE_info')
    logger4.critical('Test_dj_TEMLATE_critical')
    logger4.warning('Test_dj_TEMLATE_warning')
    logger4.error("Test_dj_TEMLATE_error")

    logger5 = logging.getLogger('django.db.backends')
    logger5.debug('Test_dj_DB_BACK_debug')
    logger5.info('Test_dj_DB_BACK_info')
    logger5.critical('Test_dj_DB_BACK_critical')
    logger5.warning('Test_dj_DB_BACK_warning')

    logger5.error("Test_dj_DB_BACK_error")

    logger6 = logging.getLogger('django.security')
    logger6.debug('Test_dj_SECURITY_debug')
    logger6.info('Test_dj_SECURITY_info')
    logger6.critical('Test_dj_SECURITY_critical')
    logger6.warning('Test_dj_SECURITY_warning')
    logger6.error("Test_dj_SECURITY_error")

    return HttpResponse('!!!!!')


class PostsList(ListView):
    model = Post
    # ordering = Post.objects.all().order_by('-public_date')
    queryset = Post.objects.all().order_by('-public_date')
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 3


class CategoryPostList(ListView):
    model = Post
    template_name = 'posts_category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('pk')
        self.category = Category.objects.get(id=category_id)

        return queryset.filter(category__id=category_id)

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['category'] = self.category
        return contex


def start(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    last_visit_date = request.session.get('last_visit_date', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    request.session['last_visit_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output = "<h2>ВСЕГО ВЫ БЫЛИ НА ЭТОЙ СТРАНИЦЕ - {0} РАЗ,</h2><h2>ДАТА ПОСЛЕДНЕГО ПОСЕЩЕНИЯ - {1}</h2>".format(
        num_visits, last_visit_date)
    return HttpResponse(output)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['is_not_author'] = not self.request.user.groups.filter(name='author').exists()
        return contex


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='author')
    if not request.user.groups.filter(name='author').exists():
        author_group.user_set.add(user)
    return redirect('user_index')


@login_required
def subscriber(request, *args, **kwargs):
    user = request.user
    category = Category.objects.get(id=kwargs.get('pk'))
    UserSubscribers.objects.create(user=user, category=category)
    return redirect('user_index')


class PostSearch(ListView):
    model = Post
    queryset = Post.objects.all().order_by('-public_date')
    template_name = 'post_search.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['filterset'] = self.filterset
        return contex


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['postcategories'] = self.object.category.all()
        return contex

    def get_object(self, *args, **kwargs):
        publication = cache.get(f'post-{self.kwargs["id"]}', None)
        # print(publication)
        if not publication:
            publication = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["id"]}', publication)
            # print(publication)
        return publication


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    # redirect_field_name = '/accounts/login/'

    def form_valid(self, form):
        user_post = form.save(commit=False)
        user_post.post_type = 'at'
        redirect_to_post = super().form_valid(form)
        send_mail_new_post.apply_async([user_post.id], countdown=5)
        return redirect_to_post


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        user_post = form.save(commit=False)
        user_post.post_type = 'nw'
        redirect_to_post = super().form_valid(form)
        send_mail_new_post.apply_async([user_post.id], countdown=5)

        return redirect_to_post


class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def form_valid(self, form):
        user_post = form.save(commit=False)
        user_post.post_type = 'at'
        return super().form_valid(form)


class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def form_valid(self, form):
        user_post = form.save(commit=False)
        user_post.post_type = 'nw'
        return super().form_valid(form)


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'article_delete.html'
    success_url = reverse_lazy('posts_list')


class NewsDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('posts_list')
