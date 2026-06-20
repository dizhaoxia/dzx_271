from rest_framework import serializers
from .models import AssessmentRecord, SubScaleRecord, FollowUpNote, PatientAssignment


class SubScaleRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubScaleRecord
        fields = ('id', 'scale_code', 'scale_name', 'total_score', 'max_score',
                  'severity', 'severity_label', 'advice', 'answers_json', 'created_at')
        read_only_fields = ('created_at',)


class FollowUpNoteSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.username', read_only=True, default='')

    class Meta:
        model = FollowUpNote
        fields = ('id', 'patient', 'professional', 'professional_name', 'record',
                  'note', 'follow_up_date', 'follow_up_type', 'next_action',
                  'created_at', 'updated_at')
        read_only_fields = ('professional', 'created_at', 'updated_at')


class PatientAssignmentSerializer(serializers.ModelSerializer):
    patient_phone = serializers.CharField(source='patient.phone', read_only=True)
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    professional_name = serializers.CharField(source='professional.username', read_only=True)

    class Meta:
        model = PatientAssignment
        fields = ('id', 'patient', 'patient_phone', 'patient_name',
                  'professional', 'professional_name', 'is_active', 'note', 'created_at')
        read_only_fields = ('created_at',)


class AssessmentRecordSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    subscale_records = SubScaleRecordSerializer(many=True, read_only=True)
    followup_notes = FollowUpNoteSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentRecord
        fields = '__all__'
        read_only_fields = ('user', 'session', 'created_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        viewer = getattr(request, 'user', None) if request else None
        # 非本人、非专业人员/管理员时对手机号脱敏
        if viewer and viewer.is_authenticated and viewer.id != instance.user_id:
            if not (viewer.is_staff or getattr(viewer, 'is_professional', False)):
                from apps.accounts.serializers import mask_phone
                ret['user_phone'] = mask_phone(instance.user.phone)
        return ret


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


class SubmitSessionSerializer(serializers.Serializer):
    """自适应会话提交：筛查答案 + 各子量表答案。"""
    screening_answers = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        required=True
    )
    subscale_answers = serializers.DictField(
        child=serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=3)),
        required=False, allow_empty=True
    )


class TrendDataSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    class Meta:
        model = AssessmentRecord
        fields = (
            'id', 'created_at', 'gsi', 'mode',
            'som_score', 'oc_score', 'is_score', 'dep_score', 'anx_score',
            'hos_score', 'phob_score', 'par_score', 'psy_score',
            'overall_risk'
        )
