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
