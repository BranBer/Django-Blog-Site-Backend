from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view
from datetime import datetime

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

import json
import os

from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes


@api_view(['POST'])
def Create_Blog_Post(request):
    #Get the token header
    authToken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
    user = Token.objects.filter(key = authToken)
    
    if(user.count() > 0):
        data = request.data
        images = []

        date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")

        blog_post = Blog_Post(
            post_title = data['post_title'], 
            author = data['author'],
            post_content = data['post_content'],
            date = date
            )

        blog_post.save()

        #Sift through images in data and create a blog post image for each 
        for key in data.keys():
            if(key[0:5] == 'image'):
                if(data[key] is not None):
                    img = Blog_Post_Image(blog_post = blog_post, image = data[key])
                    img.save()

        return JsonResponse(Blog_Post_Ser(blog_post, many = False).data, safe = False)
    else:
        return JsonResponse("Login first", safe = False)

@api_view(['POST'])
def Create_Blog_Post_By_You(request):
    data = request.data
    data._mutable = True

    if('post_content' not in data.keys()):
        return JsonResponse("Must include post_content in body", safe = False, status = 500)
    elif(data['post_content'] == ''):
        return JsonResponse("Must include post_content in body", safe = False, status = 500)

    if('post_title' not in data.keys()):
        return JsonResponse("Must include post_title in body", safe = False, status = 500)
    elif(data['post_title'] == ''):
        return JsonResponse("Must include post_title in body", safe = False, status = 500)
        
    if('author' not in data.keys()):
        data['author'] = 'anonymous'

    date = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")

    blog_post = Blog_Post(
        post_title = data['post_title'], 
        author = data['author'],
        post_content = data['post_content'],
        date = date,
        isMainPost = False,
        isVisible = False,
        )

    blog_post.save()

    return JsonResponse(Blog_Post_Ser(blog_post, many = False).data, safe = False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UpdateBlogPostVisibility(request):
    data = request.data

    if('id' in data.keys()):
        try:
            authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
            isSuperUser = Token.objects.get(key = authtoken).user.isSuperUser

            if(isSuperUser):
                blog_post = Blog_Post.objects.get(id = int(request.data['id']))
                blog_post.isVisible = not blog_post.isVisible
                blog_post.save(update_fields=['isVisible'])
            else:
                return JsonResponse('Not Authorized', safe = False, status = 500)

            return JsonResponse('Successfully Updated Post Visibility', safe = False)
        except Blog_Post.DoesNotExist:
            return JsonResponse('No Posts Found', safe = False)
        except Token.DoesNotExist:
            return JsonResponse('Not Authorized', safe = False, status = 500)

    return JsonResponse('Must include id in body')

@api_view(['POST'])
def AdminLogin(request):
    if('username' in request.data.keys() and 'password' in request.data.keys()):
        user = authenticate(username = request.data['username'], 
                            password = request.data['password'])

        if(user is not None):
            token = Token.objects.get(user = user).key

            return JsonResponse( {
                'username': user.username,
                'token': token
            }, safe = False)
        else:
            return JsonResponse("Invalid Credentials", safe = False, status = 401)

    return JsonResponse("Must Input Username and Password!", safe = False)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def DeletePost(request):
    try:
        if('id' not in request.data.keys()):
            return JsonResponse("Invalid Credentials", safe = False)

        authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
        
        isSuperUser = Token.objects.get(key = authtoken).user.isSuperUser
        
        if(isSuperUser):
            Blog_Post.objects.get(id = request.data['id']).delete()
            return JsonResponse("Successfully Deleted Post", safe = False)
        else:
            return JsonResponse("Not Authorized", safe = False, status = 500)
    except Blog_Post.DoesNotExist:
        return JsonResponse("Invalid ID", safe = False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Create_Comment(request):
    authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''
    now = datetime.now()

    try:
        user = Token.objects.get(key = authtoken).user
        user_has_posted = True if Blog_Post_Comments.objects.filter(user = user).count() > 0 else False

        if('id' in request.data.keys() and 'comment' in request.data.keys()):
            #Check if user posted in this thread already
            if(user_has_posted == False):
                comment = Blog_Post_Comments.objects.create(blog_post = Blog_Post.objects.get(id = int(request.data['id'])), user = user, comment = request.data['comment'], date_posted = now)
                ser = Blog_Post_Comments_Serializer(comment)

                return JsonResponse(ser.data, safe = False, status = 200)
        elif('comment_id' in request.data.keys() and 'comment' in request.data.keys()):
            parent_comment = Blog_Post_Comments.objects.get(id = int(request.data['comment_id']))
            
            #Check to see if a user has already replied to this comment
            user_has_replied = True if Blog_Post_Comments.objects.filter(parent = parent_comment, user = user).count() > 0 else False

            if(user_has_replied == False):
                reply = Blog_Post_Comments.objects.create(user = user, comment = request.data['comment'], parent = parent_comment, date_posted = now)

                ser = Blog_Post_Comments_Serializer(reply, many = False)

                return JsonResponse(ser.data, safe = False, status = 200)

        return JsonResponse("You can only comment once per post, and reply once per comment", safe = False, status = 500)
    except Token.DoesNotExist:
        return JsonResponse("Login first to comment", safe = False, status = 500)
    except Blog_Post.DoesNotExist:
        return JsonResponse("Invalid Blog Post ID", safe = False, status = 500)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse("Invalid Comment ID", safe = False, status = 500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Delete_Comment(request):
    authtoken = request.headers.get('Authorization')[6:] if request.headers.get('Authorization') else ''

    try:
        user = Token.objects.get(key = authtoken).user
        
        if(user.is_superuser): #If user is a superuser, they can delete any comment
            if('id' in request.data.keys()):
                deleted_comment = Blog_Post_Comments.objects.get(id = int(request.data['id'])).delete()

                return JsonResponse("Successfully Deleted Comment", safe = False)
            else: #If user is owner of comment, they can delete it
                comment =  Blog_Post_Comments.objects.get(id = int(request.data['id']))
                if(user.id == comment.user.id):
                    comment.delete() 
                    return JsonResponse("Successfully Deleted Comment", safe = False)           

        return JsonResponse("Not Authorized", safe = False, status = 500)
    except Token.DoesNotExist:
        return JsonResponse("Invalid Token", safe = False, status = 500)
    except Blog_Post_Comments.DoesNotExist:
        return JsonResponse("Comment does not exist", safe = False, status = 404)

