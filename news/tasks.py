from celery import shared_task
from django.template.loader import render_to_string

from .models import Post, User, UserSubscribers, PostCategory, Category
from django.core.mail import EmailMultiAlternatives

from datetime import datetime, timedelta


@shared_task
def send_mail_new_post(id):
    post = Post.objects.get(id=id)
    title = post.title
    text = post.text
    context = {
        'title': title,
        'text': text,
        'id': post.id,
    }

    category_id = PostCategory.objects.filter(post=post.id).all().values_list('category',
                                                                              flat=True)  # get new_post_category
    people_emails = []
    for cat in category_id:
        users_for_send_id = UserSubscribers.objects.filter(category=cat).all().values_list('user', flat=True)
        for user_id in users_for_send_id:
            user_mail = User.objects.get(id=user_id).email
            people_emails.append(user_mail)
    subject = f'В Вашей любимой категории появилась новая публикация!'

    html_content = render_to_string(
        'add_new_post.html',
        context=context,
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=post.text,
        from_email='annakhlebtsova@yandex.ru',
        to=people_emails,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_post_7_days():
    post_seven_days = Post.objects.filter(public_date__gte=datetime.now() - timedelta(days=7)).all()
    categories = []
    for post in post_seven_days:
        post_categories = post.category.all().values_list('id', flat=True)
        for i in post_categories:
            categories.append(i)
    categories_id = set(categories)

    for cat in categories_id:
        people_emails = []
        users_for_send_id = UserSubscribers.objects.filter(category=cat).all().values_list('user', flat=True)
        for user_id in users_for_send_id:
            user_mail = User.objects.get(id=user_id).email
            people_emails.append(user_mail)
        new_posts_in_category = post_seven_days.filter(category__id=cat).all()
        subject = f'В Вашей любимой категории {Category.objects.get(id=cat)} за прошедшую неделю появились новые публикации!'
        html_content = render_to_string(
            'new_post_7days.html',
            context={'posts': new_posts_in_category},
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body='posts',
            from_email='annakhlebtsova@yandex.ru',
            to=people_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
