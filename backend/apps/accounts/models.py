from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'patient', _('普通用户')
        COUNSELOR = 'counselor', _('心理咨询师')
        DOCTOR = 'doctor', _('医生')

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
    role = models.CharField(
        _('角色'),
        max_length=16,
        choices=Role.choices,
        default=Role.PATIENT,
        db_index=True,
        help_text='用户角色：普通用户/心理咨询师/医生'
    )
    title = models.CharField(_('职称/机构'), max_length=64, blank=True, default='')
    license_no = models.CharField(_('执业编号'), max_length=64, blank=True, default='')
    consent_accepted = models.BooleanField(_('已同意隐私协议'), default=False)
    consent_accepted_at = models.DateTimeField(_('同意时间'), null=True, blank=True)
    consent_version = models.CharField(_('协议版本'), max_length=16, blank=True, default='')
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

    @property
    def is_professional(self):
        return self.role in (self.Role.COUNSELOR, self.Role.DOCTOR)
