# import logging
#
# from django.conf import settings
#
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.core.management.base import BaseCommand
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
#
# from datetime import datetime, timedelta
# from news.models import Post, UserSubscribers, User, Category
# from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
#
# logger = logging.getLogger(__name__)
#
#
# def my_job():
#     post_seven_days = Post.objects.filter(public_date__gte=datetime.now() - timedelta(days=7)).all()
#     categories = []
#     for post in post_seven_days:
#         post_categories = post.category.all().values_list('id', flat=True)
#         for i in post_categories:
#             categories.append(i)
#     categories_id = set(categories)
#
#     for cat in categories_id:
#         people_emails = []
#         users_for_send_id = UserSubscribers.objects.filter(category=cat).all().values_list('user', flat=True)
#         for user_id in users_for_send_id:
#             user_mail = User.objects.get(id=user_id).email
#             people_emails.append(user_mail)
#         new_posts_in_category = post_seven_days.filter(category__id=cat).all()
#         subject = f'В Вашей любимой категории {Category.objects.get(id=cat)} за прошедшую неделю появились новые публикации!'
#         html_content = render_to_string(
#             'new_post_7days.html',
#             context={'posts': new_posts_in_category},
#         )
#
#         msg = EmailMultiAlternatives(
#             subject=subject,
#             body='posts',
#             from_email='annakhlebtsova@yandex.ru',
#             to=people_emails,
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#
#
# # функция, которая будет удалять неактуальные задачи
# def delete_old_job_executions(max_age=604_800):
#     """This job deletes all apscheduler job executions older than `max_age` from the database."""
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)
#
#
# class Command(BaseCommand):
#     help = "Runs apscheduler."
#
#     def handle(self, *args, **options):
#         scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
#         scheduler.add_jobstore(DjangoJobStore(), "default")
#
#         # добавляем работу нашему задачнику
#         scheduler.add_job(
#             my_job,
#             trigger=CronTrigger(day="*/7"),
#             # То же, что и интервал, но задача тригера таким образом более понятна django
#             id="my_job",  # уникальный айди
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info("Added job 'my_job'.")
#
#         scheduler.add_job(
#             delete_old_job_executions,
#             trigger=CronTrigger(
#                 day_of_week="mon", hour="00", minute="00"
#             ),
#             # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
#             id="delete_old_job_executions",
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info(
#             "Added weekly job: 'delete_old_job_executions'."
#         )
#
#         try:
#             logger.info("Starting scheduler...")
#             scheduler.start()
#         except KeyboardInterrupt:
#             logger.info("Stopping scheduler...")
#             scheduler.shutdown()
#             logger.info("Scheduler shut down successfully!")
