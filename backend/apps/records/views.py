from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse, Http404
from django.utils import timezone
from .models import AssessmentRecord, AssessmentSession, SubScaleRecord, FollowUpNote, PatientAssignment
from .serializers import (
    AssessmentRecordSerializer, SubmitAssessmentSerializer, TrendDataSerializer,
    SubmitSessionSerializer, SubScaleRecordSerializer,
    FollowUpNoteSerializer, PatientAssignmentSerializer
)
from apps.questionnaire.scl90_data import calculate_scores, compare_with_norm, calculate_subscale, SUBSCALES
from apps.compliance.audit import AuditLogMixin, log_access
from .comparison import compare_records
from .pdf_generator import generate_report_pdf


class IsStaffOrProfessional(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u and u.is_authenticated and (u.is_staff or getattr(u, 'is_professional', False))


def _visible_records_queryset(user):
    """患者看自己；专业人员看被分配患者；管理员看全部。"""
    if user.is_staff:
        return AssessmentRecord.objects.all().select_related('user')
    if getattr(user, 'is_professional', False):
        assigned_ids = PatientAssignment.objects.filter(
            professional=user, is_active=True
        ).values_list('patient_id', flat=True)
        return AssessmentRecord.objects.filter(user_id__in=list(assigned_ids)).select_related('user')
    return AssessmentRecord.objects.filter(user=user).select_related('user')


class AssessmentRecordViewSet(AuditLogMixin, viewsets.ModelViewSet):
    serializer_class = AssessmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('overall_risk', 'mode', 'user')
    ordering_fields = ('created_at', 'gsi', 'positive_count')
    audit_resource_type = 'record'

    def get_queryset(self):
        return _visible_records_queryset(self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    @action(detail=False, methods=['post'], url_path='submit')
    def submit_assessment(self, request):
        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data['answers']
        answers = {int(k): v for k, v in raw_answers.items()}

        scores = calculate_scores(answers)
        comparisons = compare_with_norm(scores['factor_scores'])
        fs = scores['factor_scores']

        session = AssessmentSession.objects.create(
            user=request.user, mode='classic',
            screening_items_count=len(answers), is_completed=True,
            completed_at=timezone.now()
        )
        record = AssessmentRecord.objects.create(
            user=request.user, session=session, mode='classic',
            som_score=fs.get('SOM', 0), oc_score=fs.get('O-C', 0),
            is_score=fs.get('I-S', 0), dep_score=fs.get('DEP', 0),
            anx_score=fs.get('ANX', 0), hos_score=fs.get('HOS', 0),
            phob_score=fs.get('PHOB', 0), par_score=fs.get('PAR', 0),
            psy_score=fs.get('PSY', 0), oth_score=fs.get('OTH', 0),
            gsi=scores['gsi'], positive_count=scores['positive_count'],
            positive_avg=scores['positive_avg'], total_sum=scores['total_sum'],
            answered_count=scores['answered_count'],
            answers_json={str(k): v for k, v in answers.items()},
            factors_detail=comparisons
        )
        log_access(request, 'create', 'record', record.id, detail={'mode': 'classic'})
        return Response({
            'record_id': record.id,
            **scores,
            'comparisons': comparisons,
            'overall_risk': record.overall_risk,
            'created_at': record.created_at
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='submit-session')
    def submit_session(self, request):
        """自适应会话提交：筛查答案 + 子量表答案。"""
        serializer = SubmitSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        screening_raw = serializer.validated_data['screening_answers']
        screening = {int(k): v for k, v in screening_raw.items()}
        subscale_answers = serializer.validated_data.get('subscale_answers', {}) or {}

        scores = calculate_scores(screening)
        comparisons = compare_with_norm(scores['factor_scores'])
        fs = scores['factor_scores']

        session = AssessmentSession.objects.create(
            user=request.user, mode='adaptive',
            screening_items_count=len(screening), is_completed=True,
            completed_at=timezone.now()
        )
        record = AssessmentRecord.objects.create(
            user=request.user, session=session, mode='adaptive',
            som_score=fs.get('SOM', 0), oc_score=fs.get('O-C', 0),
            is_score=fs.get('I-S', 0), dep_score=fs.get('DEP', 0),
            anx_score=fs.get('ANX', 0), hos_score=fs.get('HOS', 0),
            phob_score=fs.get('PHOB', 0), par_score=fs.get('PAR', 0),
            psy_score=fs.get('PSY', 0), oth_score=fs.get('OTH', 0),
            gsi=scores['gsi'], positive_count=scores['positive_count'],
            positive_avg=scores['positive_avg'], total_sum=scores['total_sum'],
            answered_count=scores['answered_count'],
            answers_json={str(k): v for k, v in screening.items()},
            factors_detail=comparisons
        )

        subscale_results = []
        for code, ans_raw in subscale_answers.items():
            ans = {int(k): v for k, v in ans_raw.items()}
            result = calculate_subscale(code, ans)
            name = next((s['name'] for s in SUBSCALES if s['code'] == code), code)
            sr = SubScaleRecord.objects.create(
                record=record, scale_code=code, scale_name=name,
                total_score=result['total_score'], max_score=result['max_score'],
                severity=result['severity'], severity_label=result['severity_label'],
                advice=result['advice'], answers_json=result['answers'],
            )
            subscale_results.append(SubScaleRecordSerializer(sr).data)

        # 与上一次测评对比
        prev = AssessmentRecord.objects.filter(
            user=request.user, created_at__lt=record.created_at
        ).order_by('-created_at').first()
        comparison = compare_records(prev, record) if prev else None

        log_access(request, 'create', 'record', record.id,
                   detail={'mode': 'adaptive', 'subscales': list(subscale_answers.keys())})
        return Response({
            'record_id': record.id,
            **scores,
            'comparisons': comparisons,
            'subscale_records': subscale_results,
            'comparison': comparison,
            'overall_risk': record.overall_risk,
            'created_at': record.created_at
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='trend')
    def get_trend(self, request):
        records = self.get_queryset().order_by('created_at')[:20]
        return Response(TrendDataSerializer(records, many=True).data)

    @action(detail=True, methods=['get'], url_path='detail-full')
    def get_detail_full(self, request, pk=None):
        record = self.get_object()
        serializer = self.get_serializer(record)
        log_access(request, 'view', 'record', record.id, detail={'view': 'detail-full'})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='comparison')
    def get_comparison(self, request, pk=None):
        record = self.get_object()
        prev = AssessmentRecord.objects.filter(
            user=record.user, created_at__lt=record.created_at
        ).order_by('-created_at').first()
        comp = compare_records(prev, record)
        if not comp:
            return Response({'detail': '无历史测评可供对比'})
        log_access(request, 'view', 'comparison', record.id)
        return Response(comp)

    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        record = self.get_object()
        prev = AssessmentRecord.objects.filter(
            user=record.user, created_at__lt=record.created_at
        ).order_by('-created_at').first()
        professional_view = getattr(request.user, 'is_professional', False) or request.user.is_staff
        buf = generate_report_pdf(record, prev_record=prev, professional_view=professional_view)
        log_access(request, 'export', 'record_pdf', record.id)
        resp = FileResponse(buf, as_attachment=True,
                            filename=f'scl90_report_{record.id}.pdf')
        resp['Content-Type'] = 'application/pdf'
        return resp


class FollowUpNoteViewSet(viewsets.ModelViewSet):
    """随访备注：专业人员/管理员可创建与查看分配患者的随访记录。"""
    serializer_class = FollowUpNoteSerializer
    permission_classes = [IsStaffOrProfessional]
    filterset_fields = ('patient', 'record', 'professional')
    ordering_fields = ('created_at', 'follow_up_date')

    def get_queryset(self):
        u = self.request.user
        qs = FollowUpNote.objects.all().select_related('patient', 'professional', 'record')
        if u.is_staff:
            return qs
        assigned_ids = list(PatientAssignment.objects.filter(
            professional=u, is_active=True).values_list('patient_id', flat=True))
        return qs.filter(patient_id__in=assigned_ids)

    def perform_create(self, serializer):
        note = serializer.save(professional=self.request.user)
        log_access(self.request, 'create', 'followup_note', note.id,
                   detail={'patient': note.patient_id})

    def perform_update(self, serializer):
        note = serializer.save()
        log_access(self.request, 'update', 'followup_note', note.id)


class PatientAssignmentViewSet(viewsets.ModelViewSet):
    """医患分配：管理员将患者分配给医生/咨询师。"""
    serializer_class = PatientAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrProfessional]
    queryset = PatientAssignment.objects.all().select_related('patient', 'professional')
    filterset_fields = ('professional', 'patient', 'is_active')
    ordering_fields = ('created_at',)

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        if u.is_staff:
            return qs
        return qs.filter(professional=u)

    def perform_create(self, serializer):
        obj = serializer.save()
        log_access(self.request, 'create', 'patient_assignment', obj.id,
                   detail={'patient': obj.patient_id, 'professional': obj.professional_id})
