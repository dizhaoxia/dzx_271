from django.conf import settings
from django.db import models


class ConsentRecord(models.Model):
    """用户对数据处理/隐私协议的同意授权记录（GDDR 级别留痕）。"""
    CONSENT_TYPES = [
        ('privacy', '隐私协议'),
        ('assessment', '测评数据收集'),
        ('share_professional', '共享给专业人员'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consent_records',
        verbose_name='用户'
    )
    consent_type = models.CharField('同意类型', max_length=24, choices=CONSENT_TYPES, default='privacy')
    version = models.CharField('协议版本', max_length=16)
    accepted = models.BooleanField('是否同意', default=False)
    ip_address = models.GenericIPAddressField('IP 地址', null=True, blank=True)
    user_agent = models.CharField('User-Agent', max_length=255, blank=True, default='')
    created_at = models.DateTimeField('记录时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'scl90_consent_record'
        verbose_name = '同意授权记录'
        verbose_name_plural = '同意授权记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} {self.consent_type} v{self.version} {"同意" if self.accepted else "拒绝"}'


class AuditLog(models.Model):
    """操作日志审计：所有对敏感数据的访问均可追溯。"""
    ACTION_CHOICES = [
        ('view', '查看'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
        ('login', '登录'),
        ('logout', '登出'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        verbose_name='操作人'
    )
    action = models.CharField('操作类型', max_length=16, choices=ACTION_CHOICES)
    resource_type = models.CharField('资源类型', max_length=64, blank=True, default='')
    resource_id = models.CharField('资源ID', max_length=64, blank=True, default='')
    detail = models.JSONField('详情', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('IP 地址', null=True, blank=True)
    user_agent = models.CharField('User-Agent', max_length=255, blank=True, default='')
    created_at = models.DateTimeField('操作时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'scl90_audit_log'
        verbose_name = '操作审计日志'
        verbose_name_plural = '操作审计日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user_id} {self.action} {self.resource_type} {self.created_at:%Y-%m-%d %H:%M}'
