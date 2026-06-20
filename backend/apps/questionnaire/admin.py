from django.contrib import admin
from .models import Question, NormData


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('number', 'factor', 'content_preview')
    list_filter = ('factor',)
    search_fields = ('number', 'content')
    ordering = ('number',)

    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = '题目内容'


@admin.register(NormData)
class NormDataAdmin(admin.ModelAdmin):
    list_display = ('factor', 'factor_name', 'mean', 'std')
    search_fields = ('factor', 'factor_name')
    ordering = ('factor',)
