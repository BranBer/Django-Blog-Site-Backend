from rest_framework import serializers
from blog_site.models import *

class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'display_name', 'subscribed']

class Blog_Post_Image_Ser(serializers.ModelSerializer):
    class Meta:
        model = Blog_Post_Image
        fields = ['blog_post', 'image']

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        ser = self.parent.parent.__class__(value, context=self.context)
        return ser.data

class Blog_Post_Vote_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Blog_Post_Comment_Vote
        fields = ['vote_type', 'user', 'comment']

class Blog_Post_Comments_Serializer(serializers.ModelSerializer):
    reply = RecursiveField(many = True)
    display_name = serializers.CharField(source = 'user.display_name')
    net_votes = serializers.SerializerMethodField()

    class Meta:
        model = Blog_Post_Comments
        fields = ['id', 'blog_post', 'comment', 'display_name', 'date_posted', 'net_votes', 'reply']

    def get_net_votes(self, instance):
        upvotes = instance.blog_post_comment_vote_set.filter(vote_type = True).count()
        downvotes = instance.blog_post_comment_vote_set.filter(vote_type = False).count()

        return (upvotes - downvotes)
    

class Blog_Post_Ser(serializers.ModelSerializer):   
    likes = serializers.SerializerMethodField() 
    class Meta:
        model = Blog_Post
        fields = ['id', 'post_title', 'author', 'likes', 'post_content', 'date', 'blog_post']

    def get_likes(self, instance):
        post_likes = instance.userpostlikes_set.filter().count()
        return post_likes