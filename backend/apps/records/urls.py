from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssessmentRecordViewSet, FollowUpNoteViewSet, PatientAssignmentViewSet

router = DefaultRouter()
router.register('followup-notes', FollowUpNoteViewSet, basename='followup-note')
router.register('assignments', PatientAssignmentViewSet, basename='assignment')
router.register('', AssessmentRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
]
