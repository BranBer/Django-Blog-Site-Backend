from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from femenist_blog import settings
from blog_site.managers import *


# Create your models here.

class Blog_Post(models.Model):
    post_title                          = models.CharField(max_length = 250, default = 'Enter a Post Title')
    author                              = models.CharField(max_length = 75, default = 'Enter name of the post author')
    post_content                        = models.TextField(default = 'Write some content!')
    date                                = models.DateTimeField(default = timezone.now)

class Blog_Post_Image(models.Model):
    blog_post                           = models.ForeignKey(Blog_Post, on_delete = models.CASCADE, related_name = 'blog_post')
    image                               = models.ImageField(upload_to = 'post_images/')

class User(AbstractBaseUser):
    username                        = models.CharField(verbose_name = 'username', max_length=30, blank = False, null = False, primary_key = True, unique = True)
    email                           = models.EmailField(verbose_name = 'email', blank = False, null = False, unique = True)

    first_name                      = models.CharField(max_length = 25, blank = False, null = False)
    last_name                       = models.CharField(max_length = 25, blank = False, null = False)
    date_of_birth                   = models.DateField(blank = False, null = False, default = timezone.now)
    
    date_joined                     = models.DateTimeField(verbose_name = 'date_joined', auto_now_add = True)
    last_login                      = models.DateTimeField(verbose_name = 'last_login', auto_now = True) 
    is_staff                        = models.BooleanField(default = False)
    is_admin                        = models.BooleanField(default = False)
    is_active                       = models.BooleanField(default = True)
    is_superuser                    = models.BooleanField(default = False)

    EMAIL_FIELD                     = 'email'
    USERNAME_FIELD                  = 'username'
    REQUIRED_FIELDS                 = ['email', 'first_name', 'last_name', 'date_of_birth', 'verification']

    objects                         = UserManager()
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj = None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

#Creates a token for a user each time a user is created
@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create(user = instance)