from django.urls import path
from . import views
from .views import DetailPost

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('new/', views.post_create, name='post_create'),
    path('prof/', views.post_prof, name='post_prof'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'), 
    path('image/<int:image_id>/like/', views.like_post, name='like_image'),
    path('detail/<int:pk>', DetailPost.as_view(), name='detail'), 
    path('post/<int:post_id>/reply/', views.add_reply, name='add_reply'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('image/', views.image, name='image'),
    path('image/<int:image_id>/reply/', views.add_reply, name='add_image_reply'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('following/', views.following_posts, name='following_posts'),
    path('threads/', views.thread_list, name='thread_list'),
    path('threads/new/', views.create_thread, name='create_thread'),
    path('threads/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('top', views.top, name='top'),
  
]