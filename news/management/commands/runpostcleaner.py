from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаление всех публикаций выбранного номера категории'
    missing_args_message = 'Недостаточно аргументов'

    def add_arguments(self, parser):
        parser.add_argument('argument', type=int, help='Номер категории')

    def handle(self, *args, **kwargs):
        cat_id = kwargs['argument']
        category = Category.objects.get(id=cat_id)
        self.stdout.readable()
        self.stdout.write(f'Вы действительно хотите удалить публикации категории {category}? yes/no')
        answer = input()
        if answer == 'yes':
            Post.objects.filter(category__id=cat_id).delete()

            self.stdout.write(self.style.SUCCESS('Succesfully!'))
            return

        self.stdout.write(self.style.ERROR('Access denied'))