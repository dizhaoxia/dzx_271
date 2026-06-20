from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AssessmentRecord
from .serializers import (
    AssessmentRecordSerializer, SubmitAssessmentSerializer, TrendDataSerializer
)
from apps.questionnaire.scl90_data import calculate_scores, compare_with_norm


class AssessmentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AssessmentRecord.objects.all().select_related('user')
        return AssessmentRecord.objects.filter(user=user).select_related('user')

    @action(detail=False, methods=['post'], url_path='submit')
    def submit_assessment(self, request):
        serializer = SubmitAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data['answers']
        answers = {int(k): v for k, v in raw_answers.items()}

        scores = calculate_scores(answers)
        comparisons = compare_with_norm(scores['factor_scores'])
        fs = scores['factor_scores']

        record = AssessmentRecord.objects.create(
            user=request.user,
            som_score=fs.get('SOM', 0),
            oc_score=fs.get('O-C', 0),
            is_score=fs.get('I-S', 0),
            dep_score=fs.get('DEP', 0),
            anx_score=fs.get('ANX', 0),
            hos_score=fs.get('HOS', 0),
            phob_score=fs.get('PHOB', 0),
            par_score=fs.get('PAR', 0),
            psy_score=fs.get('PSY', 0),
            oth_score=fs.get('OTH', 0),
            gsi=scores['gsi'],
            positive_count=scores['positive_count'],
            positive_avg=scores['positive_avg'],
            total_sum=scores['total_sum'],
            answers_json={str(k): v for k, v in answers.items()},
            factors_detail=comparisons
        )

        return Response({
            'record_id': record.id,
            **scores,
            'comparisons': comparisons,
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
        return Response(serializer.data)
