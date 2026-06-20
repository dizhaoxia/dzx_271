from rest_framework import serializers
from .models import Question, NormData, SubScale, SubScaleQuestion


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('number', 'content', 'factor')


class NormDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormData
        fields = ('factor', 'factor_name', 'mean', 'std', 'description')


class SubmitAnswersSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        required=True
    )

    def validate_answers(self, value):
        if len(value) != 90:
            raise serializers.ValidationError(f'需要提交90道题的答案，当前{len(value)}道')
        for i in range(1, 91):
            if str(i) not in value and i not in value:
                raise serializers.ValidationError(f'缺少第{i}题的答案')
        return value


class ScreeningSerializer(serializers.Serializer):
    """自适应首轮筛查：接受任意 SCL-90 题号(1-5) 的答案子集。"""
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        required=True
    )

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError('筛查答案不能为空')
        for k in value.keys():
            try:
                num = int(k)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f'无效的题号：{k}')
            if num < 1 or num > 90:
                raise serializers.ValidationError(f'题号超出范围：{num}')
        return value


class SubScaleQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubScaleQuestion
        fields = ('number', 'content')


class SubScaleSerializer(serializers.ModelSerializer):
    questions = SubScaleQuestionSerializer(many=True, read_only=True)
    options = serializers.SerializerMethodField()

    class Meta:
        model = SubScale
        fields = ('code', 'name', 'trigger_factor', 'description',
                  'max_score', 'questions', 'options')

    def get_options(self, obj):
        from .scl90_data import SUBSCALE_OPTIONS
        return [{'value': v, 'label': label} for v, label in SUBSCALE_OPTIONS]
