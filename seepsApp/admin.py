from .forms import ExamForm, QuestionForm, ChoiceForm
from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import *

class ChoiceInline(admin.TabularInline):
    model = Choice
    form = ChoiceForm
    can_delete = False

class QuestionResource(resources.ModelResource):
    exam = fields.Field(
        column_name='exam',
        attribute='exam',
        widget=ForeignKeyWidget(Exam, 'name')
    )

    class Meta:
        model = Question
        fields = ('content', 'exam')
        export_order = ('content', 'exam')

class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
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
admin.site.register(Exam)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Result)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Course)
admin.site.register(Tutorial)
admin.site.register(User)
admin.site.register(ExamSubmission)