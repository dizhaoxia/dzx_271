from django.contrib import admin
from .models import AssessmentRecord


@admin.register(AssessmentRecord)
class AssessmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'gsi', 'positive_count', 'overall_risk', 'created_at'
    )
    list_filter = ('overall_risk', 'created_at')
    search_fields = ('user__phone', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
