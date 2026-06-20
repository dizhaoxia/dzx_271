from rest_framework import serializers, viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Subquery, OuterRef
from django.http import HttpResponse
from django.utils import timezone
from apps.records.models import AssessmentRecord, PatientAssignment, FollowUpNote
from apps.accounts.serializers import UserSerializer, mask_phone
from apps.accounts.models import User
from apps.records.serializers import AssessmentRecordSerializer
from apps.compliance.audit import log_access
import csv
import io

User = get_user_model()


class IsStaffPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsStaffPermission]
    search_fields = ('phone', 'username', 'email')
    filterset_fields = ('gender', 'is_staff', 'is_active', 'role')
    ordering_fields = ('created_at', 'last_login')

    @action(detail=True, methods=['patch'], url_path='role')
    def set_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role')
        valid = [c[0] for c in User.Role.choices]
        if role not in valid:
            return Response({'detail': f'角色无效，可选：{valid}'}, status=status.HTTP_400_BAD_REQUEST)
        user.role = role
        user.save(update_fields=['role'])
        log_access(request, 'update', 'user_role', user.id, detail={'role': role})
        return Response(UserSerializer(user, context={'request': request}).data)


class AdminRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssessmentRecord.objects.all().select_related('user')
    serializer_class = AssessmentRecordSerializer
    permission_classes = [IsStaffPermission]
    filterset_fields = ('overall_risk', 'mode')
    search_fields = ('user__phone', 'user__username')
    ordering_fields = ('created_at', 'gsi', 'positive_count')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        records = qs.order_by('-created_at')
        log_access(request, 'export', 'records', '', detail={'format': 'csv'})

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'scl90_records_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow([
            'ID', '用户手机号(脱敏)', '用户名', '模式', '测评时间',
            '躯体化', '强迫症状', '人际关系敏感', '抑郁', '焦虑',
            '敌对', '恐怖', '偏执', '精神病性', '其他',
            'GSI总症状指数', '阳性项目数', '阳性症状均分', '总分', '整体风险'
        ])
        for r in records:
            writer.writerow([
                r.id, mask_phone(r.user.phone), r.user.username, r.mode,
                r.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                r.som_score, r.oc_score, r.is_score, r.dep_score, r.anx_score,
                r.hos_score, r.phob_score, r.par_score, r.psy_score, r.oth_score,
                r.gsi, r.positive_count, r.positive_avg, r.total_sum,
                dict(AssessmentRecord.RISK_CHOICES).get(r.overall_risk, r.overall_risk)
            ])
        return response


class DashboardStatsView(APIView):
    permission_classes = [IsStaffPermission]

    def get(self, request):
        total_users = User.objects.count()
        total_assessments = AssessmentRecord.objects.count()
        unique_assessment_users = AssessmentRecord.objects.values('user').distinct().count()
        professional_count = User.objects.filter(role__in=['counselor', 'doctor']).count()

        risk_stats = AssessmentRecord.objects.values('overall_risk').annotate(
            count=Count('id')
        ).order_by('overall_risk')
        risk_dist = {item['overall_risk']: item['count'] for item in risk_stats}

        avg_factors = AssessmentRecord.objects.aggregate(
            som_avg=Avg('som_score'), oc_avg=Avg('oc_score'),
            is_avg=Avg('is_score'), dep_avg=Avg('dep_score'),
            anx_avg=Avg('anx_score'), hos_avg=Avg('hos_score'),
            phob_avg=Avg('phob_score'), par_avg=Avg('par_score'),
            psy_avg=Avg('psy_score'), gsi_avg=Avg('gsi'),
        )

        today = timezone.now().date()
        last_30_days = [today - timezone.timedelta(days=i) for i in range(29, -1, -1)]
        daily_counts = []
        for day in last_30_days:
            count = AssessmentRecord.objects.filter(created_at__date=day).count()
            daily_counts.append({'date': day.strftime('%m-%d'), 'count': count})

        # 高危人群计数：每个用户最近一次测评风险为 red/yellow 的用户数
        latest_ids = AssessmentRecord.objects.filter(
            user=OuterRef('user')
        ).order_by('-created_at').values('pk')[:1]
        high_risk_count = AssessmentRecord.objects.filter(
            pk__in=Subquery(latest_ids), overall_risk__in=['red', 'yellow']
        ).values('user_id').distinct().count()

        log_access(request, 'view', 'dashboard', '')
        return Response({
            'total_users': total_users,
            'total_assessments': total_assessments,
            'unique_assessment_users': unique_assessment_users,
            'professional_count': professional_count,
            'high_risk_count': high_risk_count,
            'risk_distribution': {
                'green': risk_dist.get('green', 0),
                'yellow': risk_dist.get('yellow', 0),
                'red': risk_dist.get('red', 0),
            },
            'avg_factor_scores': {
                '躯体化': round(avg_factors['som_avg'] or 0, 2),
                '强迫症状': round(avg_factors['oc_avg'] or 0, 2),
                '人际关系敏感': round(avg_factors['is_avg'] or 0, 2),
                '抑郁': round(avg_factors['dep_avg'] or 0, 2),
                '焦虑': round(avg_factors['anx_avg'] or 0, 2),
                '敌对': round(avg_factors['hos_avg'] or 0, 2),
                '恐怖': round(avg_factors['phob_avg'] or 0, 2),
                '偏执': round(avg_factors['par_avg'] or 0, 2),
                '精神病性': round(avg_factors['psy_avg'] or 0, 2),
            },
            'avg_gsi': round(avg_factors['gsi_avg'] or 0, 2),
            'daily_trend_30d': daily_counts,
        })


class HighRiskListView(APIView):
    """高危人群列表：最近一次测评风险为中度及以上/轻度的用户，供管理者主动干预。"""
    permission_classes = [IsStaffPermission]

    def get(self, request):
        risk_filter = request.query_params.get('risk', 'red,yellow')
        risk_set = [r.strip() for r in risk_filter.split(',') if r.strip()]

        latest_ids = (
            AssessmentRecord.objects.filter(user=OuterRef('user'))
            .order_by('-created_at').values('pk')[:1]
        )
        latest_records = AssessmentRecord.objects.filter(
            pk__in=Subquery(latest_ids)
        ).filter(overall_risk__in=risk_set).select_related('user').order_by(
            '-gsi' if 'red' in risk_set else '-created_at'
        )

        data = []
        for r in latest_records:
            assignment = PatientAssignment.objects.filter(
                patient=r.user, is_active=True
            ).select_related('professional').first()
            data.append({
                'user_id': r.user_id,
                'username': r.user.username,
                'phone': mask_phone(r.user.phone),
                'record_id': r.id,
                'gsi': r.gsi,
                'overall_risk': r.overall_risk,
                'mode': r.mode,
                'last_assessment_time': r.created_at,
                'dep_score': r.dep_score,
                'anx_score': r.anx_score,
                'subscale_severities': [
                    {'code': s.scale_code, 'severity': s.severity, 'label': s.severity_label}
                    for s in r.subscale_records.all()
                ],
                'assigned_professional': (
                    assignment.professional.username if assignment else None
                ),
                'assigned_professional_id': (
                    assignment.professional_id if assignment else None
                ),
            })
        log_access(request, 'view', 'high_risk_list', '', detail={'count': len(data)})
        return Response({
            'total': len(data),
            'risk_filter': risk_set,
            'items': data,
        })


class ProfessionalsView(APIView):
    """专业人员列表（医生/咨询师），供分配管理。"""
    permission_classes = [IsStaffPermission]

    def get(self, request):
        pros = User.objects.filter(role__in=['counselor', 'doctor']).order_by('-created_at')
        data = []
        for p in pros:
            patient_count = PatientAssignment.objects.filter(
                professional=p, is_active=True).count()
            data.append({
                'id': p.id,
                'username': p.username,
                'phone': mask_phone(p.phone),
                'role': p.role,
                'title': p.title,
                'license_no': p.license_no,
                'patient_count': patient_count,
            })
        return Response({'total': len(data), 'items': data})
