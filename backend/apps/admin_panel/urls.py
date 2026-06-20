from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, AdminRecordViewSet, DashboardStatsView

router = DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin-user')
router.register('records', AdminRecordViewSet, basename='admin-record')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardStatsView.as_view(), name='admin-dashboard'),
]
