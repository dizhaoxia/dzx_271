from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ConsentRecordViewSet

router = DefaultRouter()
router.register('audit-logs', AuditLogViewSet, basename='audit-log')
router.register('consents', ConsentRecordViewSet, basename='consent')

urlpatterns = [
    path('', include(router.urls)),
]
