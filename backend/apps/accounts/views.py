from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    PasswordChangeSerializer, CONSENT_VERSION
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': tokens
        })

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'detail': '退出登录成功'})

    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh_token(self, request):
        try:
            refresh = RefreshToken(request.data.get('refresh'))
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        except Exception as e:
            return Response({'detail': '令牌无效或已过期'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='password-reset-request')
    def password_reset_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response({
            'detail': '验证码已发送',
            'code': result['code'],
            'phone': result['phone']
        })

    @action(detail=False, methods=['post'], url_path='password-reset-confirm')
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码重置成功'})


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        return self.put(request)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码修改成功'})


class ConsentView(APIView):
    """隐私同意授权：记录用户对数据收集与处理的同意。"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        accepted = request.data.get('accepted', False)
        if not accepted:
            return Response({'detail': '未同意协议'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.consent_accepted = True
        user.consent_accepted_at = timezone.now()
        user.consent_version = CONSENT_VERSION
        user.save(update_fields=['consent_accepted', 'consent_accepted_at', 'consent_version'])
        try:
            from apps.compliance.models import ConsentRecord
            ConsentRecord.objects.create(
                user=user,
                consent_type='privacy',
                version=CONSENT_VERSION,
                accepted=True,
                ip_address=self._client_ip(request),
            )
        except Exception:
            pass
        return Response({'detail': '已记录同意授权', 'version': CONSENT_VERSION})

    def get(self, request):
        return Response({
            'consent_accepted': request.user.consent_accepted,
            'consent_accepted_at': request.user.consent_accepted_at,
            'consent_version': request.user.consent_version,
            'current_version': CONSENT_VERSION,
            'needs_reconsent': request.user.consent_version != CONSENT_VERSION,
        })

    @staticmethod
    def _client_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
