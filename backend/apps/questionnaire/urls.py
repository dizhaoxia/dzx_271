from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, NormDataViewSet, CalculateScoreView, SubScaleViewSet, ScreeningView

router = DefaultRouter()
router.register('questions', QuestionViewSet, basename='question')
router.register('norms', NormDataViewSet, basename='norm')
router.register('subscales', SubScaleViewSet, basename='subscale')

urlpatterns = [
    path('', include(router.urls)),
    path('calculate/', CalculateScoreView.as_view(), name='calculate-score'),
    path('screening/', ScreeningView.as_view(), name='screening'),
]
