from rest_framework import serializers
from blog_site.models import *


class Blog_Post_Image_Ser(serializers.ModelSerializer):
    class Meta:
        model = Blog_Post_Image
        fields = ['blog_post', 'image']

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        ser = self.parent.parent.__class__(value, context=self.context)
        return ser.data

class Blog_Post_Comments_Serializer(serializers.ModelSerializer):
    reply = RecursiveField(many = True)
    username = serializers.CharField(source = 'user.username')
    class Meta:
        model = Blog_Post_Comments
        fields = ['id', 'blog_post', 'comment', 'username', 'reply', 'date_posted']

class Blog_Post_Ser(serializers.ModelSerializer):    
    class Meta:
        model = Blog_Post
        fields = ['id', 'post_title', 'author', 'post_content', 'date', 'blog_post']

