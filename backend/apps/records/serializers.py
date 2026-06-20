from rest_framework import serializers
from .models import AssessmentRecord


class AssessmentRecordSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AssessmentRecord
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class SubmitAssessmentSerializer(serializers.Serializer):
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


class TrendDataSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = AssessmentRecord
        fields = (
            'id', 'created_at', 'gsi',
            'som_score', 'oc_score', 'is_score', 'dep_score', 'anx_score',
            'hos_score', 'phob_score', 'par_score', 'psy_score',
            'overall_risk'
        )
