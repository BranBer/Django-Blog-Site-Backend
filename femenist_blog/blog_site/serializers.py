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

class Blog_Post_Vote_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Blog_Post_Comment_Vote
        fields = ['vote_type', 'user', 'comment']

class Blog_Post_Comments_Serializer(serializers.ModelSerializer):
    reply = RecursiveField(many = True)
    username = serializers.CharField(source = 'user.username')
    net_votes = serializers.SerializerMethodField()

    class Meta:
        model = Blog_Post_Comments
        fields = ['id', 'blog_post', 'comment', 'username', 'date_posted', 'net_votes', 'reply']

    def get_net_votes(self, instance):
        upvotes = instance.blog_post_comment_vote_set.filter(vote_type = True).count()
        downvotes = instance.blog_post_comment_vote_set.filter(vote_type = False).count()

        return (upvotes - downvotes)
    

class Blog_Post_Ser(serializers.ModelSerializer):    
    class Meta:
        model = Blog_Post
        fields = ['id', 'post_title', 'author', 'post_content', 'date', 'blog_post']

