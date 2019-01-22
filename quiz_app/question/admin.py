from django.contrib import admin
from .models import TFQuestion, MCQuestion, Answer


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'quiz', 'explanation', 'correct', 'max_time')
    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)


class AnswerInline(admin.TabularInline):
    model = Answer


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'quiz', 'explanation', 'max_time', 'answer_order')
    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(TFQuestion, TFQuestionAdmin)
