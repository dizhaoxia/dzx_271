from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="SCL-90 症状自评量表 API",
        default_version='v1',
        description="症状自测问卷与评估工具后端接口",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/questionnaire/', include('apps.questionnaire.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/admin-panel/', include('apps.admin_panel.urls')),
    path('api/compliance/', include('apps.compliance.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
