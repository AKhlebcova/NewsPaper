from django.test import TestCase
list1 = []
a = 'sgdahagahadah'
for i in a:
    list1.append(i)

print(set(list1))

from datetime import datetime, timedelta





# наша задача по выводу текста на экран

# post_seven_days = Post.objects.filter(public_date__gte = datetime.now() - timedelta(days=7)).all()


print(datetime.now() - timedelta(days=7))
