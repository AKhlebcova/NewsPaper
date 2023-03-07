from django.contrib import admin
from .models import Post, Category, PostCategory, Author


class CategoryInline(admin.TabularInline):
    model = PostCategory


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'get_public_date', 'get_categories')

    list_filter = ('author', 'post_type', 'public_date', 'category__name_of_category')
    search_fields = ('title', 'category__name_of_category')
    inlines = [
        CategoryInline,
    ]

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('post', 'category')
    list_filter = ['category']
    search_fields = ['post__title']




# Register your models here.
# admin.site.register(Post, PostAdmin)
admin.site.register(Category)
