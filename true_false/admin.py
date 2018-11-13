from django.contrib import admin
from .models import TFQuestion


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'quiz', 'explanation', 'correct', 'max_time')
    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)


admin.site.register(TFQuestion, TFQuestionAdmin)
