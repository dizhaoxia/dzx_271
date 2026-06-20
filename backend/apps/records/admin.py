from django.contrib import admin
from .models import AssessmentRecord, AssessmentSession, SubScaleRecord, FollowUpNote, PatientAssignment


@admin.register(AssessmentRecord)
class AssessmentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'mode', 'gsi', 'positive_count', 'overall_risk', 'created_at'
    )
    list_filter = ('overall_risk', 'mode', 'created_at')
    search_fields = ('user__phone', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mode', 'screening_items_count', 'is_completed', 'created_at')
    list_filter = ('mode', 'is_completed')
    ordering = ('-created_at',)


@admin.register(SubScaleRecord)
class SubScaleRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'record', 'scale_code', 'total_score', 'severity', 'created_at')
    list_filter = ('scale_code', 'severity')
    ordering = ('-created_at',)


@admin.register(FollowUpNote)
class FollowUpNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'professional', 'follow_up_date', 'created_at')
    list_filter = ('follow_up_type',)
    search_fields = ('patient__phone', 'professional__phone')
    ordering = ('-created_at',)


@admin.register(PatientAssignment)
class PatientAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'professional', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('patient__phone', 'professional__phone')
    ordering = ('-created_at',)
