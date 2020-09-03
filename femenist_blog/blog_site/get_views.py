from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes

@api_view(['GET'])
def Get_Blog_Posts(request, lowerlimit, postsPerPage):
    data = []
    posts = Blog_Post.objects.filter(isMainPost = True).order_by('-date')

    if(lowerlimit < 0): #Display first page of posts
        posts = posts[0:postsPerPage]
    elif(len(posts) - lowerlimit < postsPerPage): #Display last page of posts
        if(len(posts) - postsPerPage >= 0):
            posts = posts[len(posts) - postsPerPage: len(posts)]
        else:
            posts = posts[0: len(posts)]
    else:
        posts = posts[lowerlimit:lowerlimit+postsPerPage]
        

    for post in posts:
        post_images = Blog_Post_Image.objects.filter(blog_post = post).values('image')
        data.append(
            {
                'id': post.id,
                'post_title': post.post_title,
                'author': post.author,
                'post_content': post.post_content,
                'date': post.date,
                'isVisible': post.isVisible,
                'images': [i['image'] for i in list(post_images)]
            }
        )

    return JsonResponse(data, safe = False)


@api_view(['GET'])
def Get_Blog_Posts_By_Viewer(request, lowerlimit, postsPerPage):
    data = []

    posts = Blog_Post.objects.filter(isMainPost = False, isVisible = True).order_by('-date')                

    if(lowerlimit < 0): #Display first page of posts
        posts = posts[0:postsPerPage]
    elif(len(posts) - lowerlimit < postsPerPage):#Display last page of posts
        if(len(posts) - postsPerPage >= 0):
            posts = posts[len(posts) - postsPerPage: len(posts)]
        else:
            posts = posts[0: len(posts)]
    else:
        posts = posts[lowerlimit:lowerlimit+postsPerPage]


    for post in posts:
        data.append(
            {
                'id': post.id,
                'post_title': post.post_title,
                'author': post.author,
                'post_content': post.post_content,
                'date': post.date,
                'isVisible': post.isVisible
            }
        )

    return JsonResponse(data, safe = False)
   

@api_view(['GET'])
def Get_Blog_Post_ID(request, id):
    data = []

    try:
        post = Blog_Post.objects.get(id = id)
        images = []

        if(post.isMainPost):
            post_images = Blog_Post_Image.objects.filter(blog_post = post).values('image')
            images = [i['image'] for i in list(post_images)]

        data.append(
            {
                'id': post.id,
                'post_title': post.post_title,
                'author': post.author,
                'post_content': post.post_content,
                'date': post.date,
                'images': images
            }
        )

        return JsonResponse(data, safe = False)

    except Blog_Post.DoesNotExist:
        return JsonResponse({}, safe = False)

    return JsonResponse({}, safe = False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Get_Blog_Post_Comments(request, id):
    try:
        post = Blog_Post.objects.get(id = int(id))
        post_comments = Blog_Post_Comments.objects.filter(blog_post = post)

        ser = Blog_Post_Comments_Serializer(post_comments, many = True)

        return JsonResponse(ser.data, safe = False)
    except Blog_Post.DoesNotExist:
        return JsonResponse("Invalid Blog Post ID", safe = False, status = 404)