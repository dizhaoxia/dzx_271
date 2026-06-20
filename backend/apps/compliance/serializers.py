from rest_framework import serializers
from .models import AuditLog, ConsentRecord


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')
    user_phone = serializers.CharField(source='user.phone', read_only=True, default='')
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'username', 'user_phone', 'action', 'action_display',
                  'resource_type', 'resource_id', 'detail', 'ip_address',
                  'user_agent', 'created_at')


class ConsentRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = ConsentRecord
        fields = ('id', 'user', 'username', 'consent_type', 'version',
                  'accepted', 'ip_address', 'created_at')
