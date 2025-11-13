from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'username', 'role', 'created_at']
    list_filter = ['role']
    search_fields = ['email', 'username']
