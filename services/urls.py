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
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('make_appointment/<int:post_id>/', views.make_appointment, name='make_appointment'),
    path('appointment_confirmation/<int:appointment_id>/',
         views.appointment_confirmation, name='appointment_confirmation'),
    path('my_posts/', views.my_posts, name='my_posts'),
    path('my_appointments/', views.my_appointments, name='my_appointments'),
    path('complete_appointment/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('profile/', views.view_profile, name='profile'),
]
