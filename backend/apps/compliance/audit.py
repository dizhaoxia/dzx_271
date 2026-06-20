"""审计日志辅助工具：在敏感操作处调用 log_access 留痕。"""
import json
from .models import AuditLog


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    ip = request.META.get('REMOTE_ADDR')
    return ip or None


def log_access(request, action, resource_type='', resource_id='', detail=None):
    """记录一条审计日志。失败静默，不影响业务流程。"""
    try:
        user = getattr(request, 'user', None) if request else None
        user_id = user.id if user and getattr(user, 'is_authenticated', False) else None
        if user_id is None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = None
        ua = ''
        if request is not None:
            ua = request.META.get('HTTP_USER_AGENT', '')[:255]
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else '',
            detail=detail or {},
            ip_address=_client_ip(request),
            user_agent=ua,
        )
    except Exception:
        pass


class AuditLogMixin:
    """为 ViewSet 注入自动审计：在 retrieve/list/export 等动作后记录访问。"""

    audit_resource_type = 'record'
    audit_actions = {
        'list': 'view',
        'retrieve': 'view',
        'export_csv': 'export',
        'get_detail_full': 'view',
        'get_trend': 'view',
    }

    def _audit(self, request, action_key, obj=None):
        action = self.audit_actions.get(action_key)
        if not action:
            return
        resource_id = obj.id if obj is not None else ''
        log_access(request, action, self.audit_resource_type, resource_id,
                   detail={'view': action_key})

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        try:
            self._audit(request, 'retrieve', self.get_object())
        except Exception:
            pass
        return resp

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        self._audit(request, 'list')
        return resp
