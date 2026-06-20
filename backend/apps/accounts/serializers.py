from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache
import random

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, max_length=128)
    confirm_password = serializers.CharField(write_only=True, min_length=6, max_length=128)

    class Meta:
        model = User
        fields = ('phone', 'password', 'confirm_password', 'username', 'email', 'gender', 'age')
        extra_kwargs = {
            'username': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password': '两次密码输入不一致'})
        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({'phone': '该手机号已注册'})
        return attrs

    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = f'用户{validated_data["phone"]}'
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
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
    class Meta:
        model = User
        fields = ('id', 'phone', 'username', 'email', 'gender', 'age', 'avatar', 'is_staff', 'is_active', 'created_at')
        read_only_fields = ('id', 'phone', 'is_staff', 'is_active', 'created_at')


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
