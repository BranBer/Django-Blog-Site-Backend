from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

@api_view(['GET'])
def Get_Blog_Posts(request, lowerlimit, upperlimit):
    data = []
    posts = Blog_Post.objects.filter(isMainPost = True)[lowerlimit:upperlimit]

    for post in posts:
        post_images = Blog_Post_Image.objects.filter(blog_post = post).values('image')
        data.append(
            {
                'id': post.id,
                'post_title': post.post_title,
                'author': post.author,
                'post_content': post.post_content,
                'date': post.date,
                'images': [i['image'] for i in list(post_images)]
            }
        )

    return JsonResponse(data, safe = False)


@api_view(['POST'])
def Get_Blog_Posts_By_Viewer(request, lowerlimit, upperlimit):
    data = []
    

    if('isVisible' in request.data.keys()):
        visibility = request.data['isVisible'].rstrip()

        posts = Blog_Post.objects.filter(isMainPost = False, isVisible = visibility).order_by('-date')                

        if(lowerlimit >= 0 and lowerlimit < posts.count() and upperlimit >= lowerlimit and upperlimit <= posts.count()):
            body = request.data
            if('PullFromEndpoint' in body.keys()):
                if(body['PullFromEndpoint'] == "Last"):
                    posts = posts[posts.count() - 1 - lowerlimit:posts.count() - 1]
                    data.append({'position': posts.count() - lowerlimit})
                if(body['PullFromEndpoint'] == "First"):
                    posts = posts[0: upperlimit]
            else:
                posts = posts[lowerlimit:upperlimit]
        else:
            return JsonResponse('Out of Bounds', safe = False, status = 500)

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
   
    return JsonResponse('Must Include isVisible Parameter is Body', safe = False)


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

