from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'username', 'email', 'gender', 'age', 'is_staff', 'is_active', 'created_at')
    list_filter = ('gender', 'is_staff', 'is_active', 'created_at')
    search_fields = ('phone', 'username', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
