"""femenist_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog_site.get_views import *
from blog_site.post_views import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/<int:lowerlimit>/<int:upperlimit>/', Get_Blog_Posts),
    path('posts/<int:id>/', Get_Blog_Post_ID),
    path('posts/ByYou/<int:lowerlimit>/<int:upperlimit>/', Get_Blog_Posts_By_Viewer),
    path('posts/ByYou/UpdateVisibility/', UpdateBlogPostVisibility),
    path('posts/delete/', DeletePost),
    path('create/', Create_Blog_Post),
    path('login/', AdminLogin),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

