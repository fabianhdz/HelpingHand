# URLs for the website

from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup_user, name='signup_user'),
    path('signup/profile/', views.signup_profile, name='signup_profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('posts-feed/', views.posts_feed, name='posts_feed'),
]
