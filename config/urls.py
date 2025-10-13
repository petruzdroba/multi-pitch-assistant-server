from django.contrib import admin
from django.urls import path
from multipitch.views.auth_views import SignupView, LoginView, MeView
from multipitch.views.backup_views import BackupUploadView, BackupRetrieveView
from multipitch.views.token_view import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path("backup/upload/", BackupUploadView.as_view(), name="backup-upload"),
    path("backup/download/", BackupRetrieveView.as_view(), name="backup-download"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
