from django import forms
from django.core.exceptions import ValidationError
from .models import Post


class PostForm(forms.ModelForm):
    title = forms.CharField(min_length=6, label='Заголовок')
    text = forms.CharField(min_length=100, label='Текст публикации')

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'author',
            'category',
        ]

        labels = {
            'author': ('Ваш username'),
            'category': ('Ключевое слово'),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        title = cleaned_data.get('title')
        if title == text:
            raise ValidationError(
                'Содержание публикации не должно совпадать с названием'
            )

        return cleaned_data
