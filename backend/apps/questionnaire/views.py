from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Question, NormData, SubScale
from .serializers import (
    QuestionSerializer, NormDataSerializer, SubmitAnswersSerializer,
    ScreeningSerializer, SubScaleSerializer
)
from .scl90_data import (
    calculate_scores, compare_with_norm, recommend_subscales,
    SCREENING_ITEMS, SUBSCALE_QUESTIONS, calculate_subscale
)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'number'

    @action(detail=False, methods=['get'], url_path='page/(?P<page_num>\d+)')
    def get_by_page(self, request, page_num=None):
        page_size = 10
        try:
            page = int(page_num)
        except (TypeError, ValueError):
            return Response({'detail': '页码无效'}, status=status.HTTP_400_BAD_REQUEST)
        if page < 1 or page > 9:
            return Response({'detail': '页码范围为1-9'}, status=status.HTTP_400_BAD_REQUEST)
        start = (page - 1) * page_size + 1
        end = start + page_size - 1
        questions = self.get_queryset().filter(number__gte=start, number__lte=end)
        return Response({
            'page': page,
            'total_pages': 9,
            'page_size': page_size,
            'total': 90,
            'questions': QuestionSerializer(questions, many=True).data
        })

    @action(detail=False, methods=['get'], url_path='all')
    def get_all(self, request):
        questions = self.get_queryset()
        return Response({
            'total': questions.count(),
            'questions': QuestionSerializer(questions, many=True).data
        })

    @action(detail=False, methods=['get'], url_path='screening-items')
    def screening_items(self, request):
        """返回自适应首轮筛查题号及题目内容。"""
        qs = {q.number: q.content for q in self.get_queryset().filter(number__in=SCREENING_ITEMS)}
        items = [{'number': n, 'content': qs.get(n, ''), 'factor': 'SCL90'} for n in SCREENING_ITEMS]
        return Response({
            'total': len(items),
            'questions': items,
        })


class NormDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NormData.objects.all()
    serializer_class = NormDataSerializer
    permission_classes = [permissions.AllowAny]


class SubScaleViewSet(viewsets.ReadOnlyModelViewSet):
    """自适应子量表（PHQ-9 / GAD-7）题目与说明。"""
    queryset = SubScale.objects.all().prefetch_related('questions')
    serializer_class = SubScaleSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'code'

    @action(detail=True, methods=['get'], url_path='questions')
    def questions(self, request, code=None):
        subscale = self.get_object()
        from .scl90_data import SUBSCALE_OPTIONS
        data = SubScaleSerializer(subscale).data
        data['options'] = [{'value': v, 'label': l} for v, l in SUBSCALE_OPTIONS]
        return Response(data)


class CalculateScoreView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubmitAnswersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data['answers']
        answers = {}
        for k, v in raw_answers.items():
            answers[int(k)] = v
        scores = calculate_scores(answers)
        comparisons = compare_with_norm(scores['factor_scores'])
        return Response({
            **scores,
            'comparisons': comparisons
        })


class ScreeningView(APIView):
    """自适应首轮筛查：根据 SCL-90 答案子集计算因子严重度，推荐追加的子量表。"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ScreeningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data['answers']
        answers = {int(k): v for k, v in raw_answers.items()}
        scores = calculate_scores(answers)
        comparisons = compare_with_norm(scores['factor_scores'])
        recommended = recommend_subscales(scores['factor_scores'], comparisons)
        # 附带推荐子量表的题目
        recommended_with_questions = []
        for r in recommended:
            r_copy = dict(r)
            r_copy['questions'] = [
                {'number': n, 'content': c} for n, c in SUBSCALE_QUESTIONS.get(r['code'], [])
            ]
            recommended_with_questions.append(r_copy)
        return Response({
            **scores,
            'comparisons': comparisons,
            'recommended_subscales': recommended_with_questions,
            'screening_items_count': len(answers),
        })
