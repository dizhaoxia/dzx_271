from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentRecordViewSet

router = DefaultRouter()
router.register('', AssessmentRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
]
