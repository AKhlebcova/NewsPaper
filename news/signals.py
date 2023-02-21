from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# from .models import Post, User, UserSubscribers, PostCategory, Category
# from django.core.mail import EmailMultiAlternatives
#
# from django.template.loader import render_to_string
#
#
# @receiver(m2m_changed, sender=Post.category.through)
# def news_category_sender(sender, instance, action, **kwargs):
#     if action != "post_add":
#         return
#     post_id = instance.id
#     title = Post.objects.get(id=post_id).title
#     text = Post.objects.get(id=post_id).text
#     context = {
#         'title': title,
#         'text': text,
#         'id': post_id,
#     }
#
#     category_id = PostCategory.objects.filter(post=post_id).all().values_list('category',
#                                                                               flat=True)  # get new_post_category
#     people_emails = []
#     for cat in category_id:
#         users_for_send_id = UserSubscribers.objects.filter(category=cat).all().values_list('user', flat=True)
#         for user_id in users_for_send_id:
#             user_mail = User.objects.get(id=user_id).email
#             people_emails.append(user_mail)
#     subject = f'В Вашей любимой категории появилась новая публикация!'
#
#     html_content = render_to_string(
#         'add_new_post.html',
#         context=context,
#     )
#     msg = EmailMultiAlternatives(
#         subject=subject,
#         body=instance.text,
#         from_email='annakhlebtsova@yandex.ru',
#         to=people_emails,
#     )
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
