from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from femenist_blog import settings
from blog_site.managers import *

# Create your models here.
class Blog_Post(models.Model):
    post_title                          = models.CharField(max_length = 250, default = 'Enter a Post Title')
    author                              = models.CharField(max_length = 75, default = 'Enter name of the post author')
    post_content                        = models.TextField(default = 'Write some content!')
    date                                = models.DateTimeField(default = timezone.now)
    isMainPost                          = models.BooleanField(default = True)
    isVisible                           = models.BooleanField(default = True)

class Blog_Post_Image(models.Model):
    blog_post                           = models.ForeignKey(Blog_Post, on_delete = models.CASCADE, related_name = 'blog_post')
    image                               = models.ImageField(upload_to = 'post_images/')

class User(AbstractBaseUser):
    username                        = models.CharField(verbose_name = 'username', max_length=30, blank = False, null = False, primary_key = True, unique = True)
    email                           = models.EmailField(verbose_name = 'email', blank = False, null = False, unique = True)
    display_name                    = models.CharField(verbose_name = 'display_name', max_length = 50, blank = False, default = 'Not Set', null = False, unique = False)

    date_of_birth                   = models.DateField(blank = False, null = False, default = timezone.now)
    
    date_joined                     = models.DateTimeField(verbose_name = 'date_joined', auto_now_add = True)
    last_login                      = models.DateTimeField(verbose_name = 'last_login', auto_now = True) 
    is_staff                        = models.BooleanField(default = False)
    is_admin                        = models.BooleanField(default = False)
    is_active                       = models.BooleanField(default = True)
    is_superuser                    = models.BooleanField(default = False)

    EMAIL_FIELD                     = 'email'
    USERNAME_FIELD                  = 'username'
    REQUIRED_FIELDS                 = ['email', 'date_of_birth']

    objects                         = UserManager()
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj = None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        return email

class UserPostLikes(models.Model):
    user                                = models.ForeignKey(User, on_delete = models.CASCADE)
    post                                = models.ForeignKey(Blog_Post, on_delete = models.CASCADE)

class EmailCodes(models.Model):
    code                                = models.CharField(max_length = 6, unique = True, null = False)
    email                               = models.EmailField(unique = True, null = False)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        return email

class ChangeEmailCodes(models.Model):
    code                                = models.CharField(max_length = 6, unique = True, null = False)
    user                                = models.OneToOneField(User, null = False, on_delete = models.CASCADE)
    new_email                           = models.EmailField(unique = True, null = False)

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email'].lower()
        return new_email

class ChangePasswordCodes(models.Model):
    user                                = models.OneToOneField(User, on_delete = models.CASCADE)
    code                                = models.CharField(max_length = 6, unique = True, null = False)

class Blog_Post_Comments(models.Model):
    user                                = models.ForeignKey(User, on_delete = models.CASCADE)
    blog_post                           = models.ForeignKey(Blog_Post, on_delete = models.CASCADE, default = None, null = True)
    comment                             = models.TextField(max_length = 250, default = '')
    parent                              = models.ForeignKey('self', on_delete = models.CASCADE, null = True, related_name = "reply")
    date_posted                         = models.DateTimeField(null = True)

#The Vote is an upvote if vote_type is true. The vote is a downvote if vote_type is false.
class Blog_Post_Comment_Vote(models.Model):
    vote_type                           = models.BooleanField(default = True)
    user                                = models.ForeignKey(User, null = True, on_delete = models.DO_NOTHING)
    comment                             = models.ForeignKey(Blog_Post_Comments, null = True, on_delete = models.CASCADE)
    
#Creates a token for a user each time a user is created
@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user = instance)

    