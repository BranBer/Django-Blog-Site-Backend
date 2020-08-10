from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view

@api_view(['GET'])
def Get_Blog_Posts(request, lowerlimit, upperlimit):
    data = []
    posts = Blog_Post.objects.filter()[lowerlimit:upperlimit]

    for post in posts:
        post_images = Blog_Post_Image.objects.filter(blog_post = post).values('image')
        data.append(
            {
                'post_title': post.post_title,
                'author': post.author,
                'post_content': post.post_content,
                'date': post.date,
                'images': [i['image'] for i in list(post_images)]
            }
        )

    return JsonResponse(data, safe = False)