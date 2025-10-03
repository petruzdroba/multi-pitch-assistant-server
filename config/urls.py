from django.contrib import admin
from django.urls import path
from multipitch.views.auth_views import SignupView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),  
]
