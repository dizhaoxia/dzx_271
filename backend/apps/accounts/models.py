from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    phone = models.CharField(
        _('手机号'),
        max_length=11,
        unique=True,
        db_index=True,
        help_text='用户手机号，用于登录'
    )
    avatar = models.ImageField(
        _('头像'),
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    gender = models.CharField(
        _('性别'),
        max_length=10,
        choices=[('male', '男'), ('female', '女'), ('other', '其他')],
        default='other'
    )
    age = models.PositiveIntegerField(_('年龄'), null=True, blank=True)
    created_at = models.DateTimeField(_('注册时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        db_table = 'scl90_user'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} ({self.username})'
