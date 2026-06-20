from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Question, NormData
from .serializers import QuestionSerializer, NormDataSerializer, SubmitAnswersSerializer
from .scl90_data import calculate_scores, compare_with_norm


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


class NormDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NormData.objects.all()
    serializer_class = NormDataSerializer
    permission_classes = [permissions.AllowAny]


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
