from django.contrib import admin
from .models import Answer, MCQuestion


class AnswerInline(admin.TabularInline):
    model = Answer


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'quiz', 'explanation', 'answer_order')
    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


admin.site.register(MCQuestion, MCQuestionAdmin)
