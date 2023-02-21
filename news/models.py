from django.db import models
from django.urls import reverse
from django import forms
from django.contrib.auth.models import User, Group
from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm


class UserSubscribers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    # def __str__(self):
    #     return self.user.username


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        post_rating = 0
        post_comments_rating = 0
        summ_comment_rating = 0

        for val in self.post_set.all().values('post_rating'):
            for key in val:
                post_rating = post_rating + val[key]

        for val in Comment.objects.filter(user_id=self.user_id).all().values('comment_rating'):
            for key in val:
                summ_comment_rating += val[key]

        for post in self.post_set.all():
            post_comments_rating += post.comments_rating()

        self.user_rating = post_rating * 3 + post_comments_rating + summ_comment_rating
        self.save()


class Category(models.Model):
    name_of_category = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name_of_category

    def get_id(self):
        return self.id


class Post(models.Model):
    article = 'at'
    news = 'nw'
    POSITIONS = [
        (article, 'статья'),
        (news, 'новость')
    ]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POSITIONS, default=article)
    public_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=64, unique=True)
    text = models.CharField(max_length=3000)
    post_rating = models.IntegerField(default=0)

    # def __str__(self):
    #     username = User.objects.filter(id=self.author.user_id).first().username
    #     return f'{self.title}' \
    #            f'{self.preview()}' \
    #            f'{username}' \
    #            f'{self.get_public_date()}'

    def get_public_date(self):
        return self.public_date.strftime('%Y-%m-%d')

    def preview(self):
        if len(self.text) <= 124:
            return f'{self.text}...'
        return f'{self.text[0:124]}...'

    def like_to_author(self):
        self.post_rating += 1
        self.save()

    def dislike_to_author(self):
        self.post_rating -= 1
        self.save()

    def comments_rating(self):
        query = Comment.objects.filter(post_id=self.id).all()
        comments_rating = 0
        for val in query:
            comments_rating += val.comment_rating
        return comments_rating

    # def get_info(self):
    #     username = User.objects.filter(id=self.author.user_id).first().username
    #     return f'{self.public_date}, {username}, {self.post_rating}, {self.title}, {self.preview()}'
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    # def __str__(self):
    #     return f'{self.title}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=512)
    comment_date = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like_to_user(self):
        self.comment_rating += 1
        self.save()

    def dislike_to_user(self):
        self.comment_rating -= 1
        self.save()


class CommonSignupForm(SignupForm):

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
