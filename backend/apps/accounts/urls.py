from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserProfileView, PasswordChangeView

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
]
