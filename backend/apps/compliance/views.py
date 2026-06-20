from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AuditLog, ConsentRecord
from .serializers import AuditLogSerializer, ConsentRecordSerializer
from apps.admin_panel.views import IsStaffPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作审计日志：仅管理员可查看，所有访问记录可追溯。"""
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [IsStaffPermission]
    filterset_fields = ('action', 'resource_type', 'user')
    ordering_fields = ('created_at',)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        from django.db.models import Count
        qs = self.filter_queryset(self.get_queryset())
        by_action = qs.values('action').annotate(count=Count('id'))
        by_resource = qs.values('resource_type').annotate(count=Count('id'))
        return Response({
            'total': qs.count(),
            'by_action': {item['action']: item['count'] for item in by_action},
            'by_resource': {item['resource_type']: item['count'] for item in by_resource},
        })


class ConsentRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """同意授权记录：仅管理员可查看。"""
    queryset = ConsentRecord.objects.all().select_related('user')
    serializer_class = ConsentRecordSerializer
    permission_classes = [IsStaffPermission]
    filterset_fields = ('consent_type', 'accepted')
    ordering_fields = ('created_at',)
