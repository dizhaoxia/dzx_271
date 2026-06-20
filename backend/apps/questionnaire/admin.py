from django.contrib import admin
from .models import Question, NormData, SubScale, SubScaleQuestion


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


class SubScaleQuestionInline(admin.TabularInline):
    model = SubScaleQuestion
    extra = 0
    ordering = ('number',)


@admin.register(SubScale)
class SubScaleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'trigger_factor', 'max_score')
    search_fields = ('code', 'name')
    ordering = ('code',)
    inlines = [SubScaleQuestionInline]
