from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
]