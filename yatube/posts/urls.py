from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='main'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create/', views.post_create, name='create'),
    path('posts/<post_id>/edit/', views.post_edit, name='edit'),
    path('posts/<post_id>/delete/', views.post_delete, name='delete'),
    path('posts/<int:post_id>/comment/', views.add_comments, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path('profile/<str:username>/follow/', views.profile_follow, name='profile_follow'),
    path('profile/<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow')
]
