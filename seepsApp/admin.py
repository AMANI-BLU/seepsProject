# admin.py
from django.contrib import admin
from .models import *
from .forms import ExamForm, QuestionForm, ChoiceForm

class ChoiceInline(admin.TabularInline):
    model = Choice
    form = ChoiceForm
    extra = 4
    max_num = 4
    can_delete = False

class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    inlines = [ChoiceInline]
    list_display = ['content', 'exam']

class ExamAdmin(admin.ModelAdmin):
    form = ExamForm
    list_display = ['name', 'timer', 'department_name']

class ChoiceAdmin(admin.ModelAdmin):
    form = ChoiceForm
    list_display = ['text', 'is_correct', 'question']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback_text', 'created_at']

# Register your models and admin classes
admin.site.register(Exam, ExamAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Result)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Course)
admin.site.register(Tutorial)
admin.site.register(User)