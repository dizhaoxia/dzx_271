from rest_framework import serializers
from .models import Question, NormData


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
