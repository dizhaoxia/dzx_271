from rest_framework import serializers, viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.utils import timezone
from apps.records.models import AssessmentRecord
from apps.accounts.serializers import UserSerializer
from apps.records.serializers import AssessmentRecordSerializer
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
    filterset_fields = ('gender', 'is_staff', 'is_active')
    ordering_fields = ('created_at', 'last_login')


class AdminRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AssessmentRecord.objects.all().select_related('user')
    serializer_class = AssessmentRecordSerializer
    permission_classes = [IsStaffPermission]
    filterset_fields = ('overall_risk',)
    search_fields = ('user__phone', 'user__username')
    ordering_fields = ('created_at', 'gsi', 'positive_count')

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        records = qs.order_by('-created_at')

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'scl90_records_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow([
            'ID', '用户手机号', '用户名', '测评时间',
            '躯体化', '强迫症状', '人际关系敏感', '抑郁', '焦虑',
            '敌对', '恐怖', '偏执', '精神病性', '其他',
            'GSI总症状指数', '阳性项目数', '阳性症状均分', '总分', '整体风险'
        ])
        for r in records:
            writer.writerow([
                r.id, r.user.phone, r.user.username,
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

        risk_stats = AssessmentRecord.objects.values('overall_risk').annotate(
            count=Count('id')
        ).order_by('overall_risk')
        risk_dist = {item['overall_risk']: item['count'] for item in risk_stats}

        avg_factors = AssessmentRecord.objects.aggregate(
            som_avg=Avg('som_score'),
            oc_avg=Avg('oc_score'),
            is_avg=Avg('is_score'),
            dep_avg=Avg('dep_score'),
            anx_avg=Avg('anx_score'),
            hos_avg=Avg('hos_score'),
            phob_avg=Avg('phob_score'),
            par_avg=Avg('par_score'),
            psy_avg=Avg('psy_score'),
            gsi_avg=Avg('gsi'),
        )

        today = timezone.now().date()
        last_30_days = [today - timezone.timedelta(days=i) for i in range(29, -1, -1)]
        daily_counts = []
        for day in last_30_days:
            count = AssessmentRecord.objects.filter(
                created_at__date=day
            ).count()
            daily_counts.append({'date': day.strftime('%m-%d'), 'count': count})

        return Response({
            'total_users': total_users,
            'total_assessments': total_assessments,
            'unique_assessment_users': unique_assessment_users,
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
