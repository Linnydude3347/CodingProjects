from django.contrib import admin
from django.urls import path, include
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password-reset
    path('accounts/signup/', blog_views.signup, name='signup'),
    path('', include('blog.urls')),
]