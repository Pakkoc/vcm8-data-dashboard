from django.db import models
import uuid


class UserRole(models.TextChoices):
    ADMIN = 'admin', '관리자'
    GENERAL = 'general', '일반 사용자'


class Profile(models.Model):
    """Supabase Auth 사용자와 연결되는 프로필"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.GENERAL
    )
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
