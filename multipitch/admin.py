from django.contrib import admin
from .models import UserAuth, UserBackup

@admin.register(UserAuth)
class UserAuthAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "created_at", "updated_at")
    search_fields = ("username", "email")


@admin.register(UserBackup)
class UserBackupAdmin(admin.ModelAdmin):
    list_display = ("user", "last_sync")
    search_fields = ("user__username",)
