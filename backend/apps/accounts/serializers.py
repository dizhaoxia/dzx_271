from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
import random

User = get_user_model()

CONSENT_VERSION = '2025.1'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=128)
    confirm_password = serializers.CharField(write_only=True, min_length=6, max_length=128)
    consent_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ('phone', 'password', 'confirm_password', 'username', 'email',
                 'gender', 'age', 'role', 'title', 'license_no', 'consent_accepted')
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'role': {'required': False},
            'title': {'required': False, 'allow_blank': True},
            'license_no': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({'phone': '该手机号已注册'})
        if not attrs.get('consent_accepted'):
            raise serializers.ValidationError({'consent_accepted': '必须同意隐私协议才能注册'})
        role = attrs.get('role', User.Role.PATIENT)
        if role in (User.Role.COUNSELOR, User.Role.DOCTOR) and not attrs.get('license_no'):
            raise serializers.ValidationError({'license_no': '专业用户须填写执业编号'})
        return attrs

    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = f'用户{validated_data["phone"]}'
        password = validated_data.pop('password')
        consent = validated_data.pop('consent_accepted', False)
        user = User(**validated_data)
        user.set_password(password)
        if consent:
            user.consent_accepted = True
            user.consent_accepted_at = timezone.now()
            user.consent_version = CONSENT_VERSION
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, max_length=11)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone=attrs['phone'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone': '用户不存在'})
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError({'password': '密码错误'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': '账号已被禁用'})
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    is_professional = serializers.BooleanField(source='is_professional', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'username', 'email', 'gender', 'age', 'avatar',
                 'is_staff', 'is_active', 'role', 'title', 'license_no',
                 'consent_accepted', 'consent_accepted_at', 'consent_version',
                 'is_professional', 'created_at')
        read_only_fields = ('id', 'phone', 'is_staff', 'is_active', 'created_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # 非本人且非专业人员/管理员时，对手机号脱敏
        request = self.context.get('request')
        viewer = getattr(request, 'user', None)
        if viewer and viewer.is_authenticated and viewer.id != instance.id:
            if not (viewer.is_staff or getattr(viewer, 'is_professional', False)):
                ret['phone'] = mask_phone(instance.phone)
        return ret


def mask_phone(phone):
    """对手机号进行 GDPR 级别脱敏：保留前3后2。"""
    if not phone or len(phone) < 6:
        return phone
    return f'{phone[:3]}{"*" * (len(phone) - 5)}{phone[-2:]}'


class PasswordResetRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, max_length=11)

    def validate_phone(self, value):
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号未注册')
        return value

    def create(self, validated_data):
        phone = validated_data['phone']
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        cache.set(f'password_reset:{phone}', code, timeout=300)
        return {'phone': phone, 'code': code}


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        cached_code = cache.get(f'password_reset:{attrs["phone"]}')
        if not cached_code or cached_code != attrs['code']:
            raise serializers.ValidationError({'code': '验证码错误或已过期'})
        try:
            user = User.objects.get(phone=attrs['phone'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone': '用户不存在'})
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        cache.delete(f'password_reset:{self.validated_data["phone"]}')
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': '原密码错误'})
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
