from rest_framework import serializers
from blog_site.models import *


class Blog_Post_Image_Ser(serializers.ModelSerializer):
    class Meta:
        model = Blog_Post_Image
        fields = ['blog_post', 'image']


class Blog_Post_Ser(serializers.ModelSerializer):
    blog_post = Blog_Post_Image_Ser(many = True)

    class Meta:
        model = Blog_Post
        fields = ['post_title', 'author', 'post_content', 'date', 'blog_post']

