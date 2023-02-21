import django_filters
from django_filters import FilterSet, ModelMultipleChoiceFilter
from .models import Post, Category
from django.forms import DateTimeInput


class PostFilter(FilterSet):
    post_category = ModelMultipleChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Ключевое слово',
        conjoined=True,
    )

    after_date = django_filters.DateTimeFilter(
        field_name='public_date',
        lookup_expr='gte',
        label='Дата',
        widget=DateTimeInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
        }
