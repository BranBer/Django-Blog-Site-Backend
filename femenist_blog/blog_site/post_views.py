from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view
from datetime import datetime

@api_view(['POST'])
def Create_Blog_Post(request):
    data = request.data
    images = []

    data['date'] = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")

    blog_post = Blog_Post(
        post_title = data['post_title'], 
        author = data['author'],
        post_content = data['post_content'],
        date = data['date']
        )

    blog_post.save()

    #Sift through images in data and create a blog post image for each 
    for key in data.keys():
        if(key[0:5] == 'image'):
            img = Blog_Post_Image(blog_post = blog_post, image = data[key])
            img.save()

    return JsonResponse(Blog_Post_Ser(blog_post, many = False).data, safe = False)
