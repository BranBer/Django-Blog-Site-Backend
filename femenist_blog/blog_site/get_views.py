from django.shortcuts import render
from django.http import JsonResponse
from blog_site.models import *
from blog_site.serializers import *
from rest_framework.decorators import api_view

@api_view(['GET'])
def Get_Blog_Posts(request):
    posts = Blog_Post.objects.all()

    ser = Blog_Post_Ser(posts, many = True)

    return JsonResponse(ser.data, safe = False)