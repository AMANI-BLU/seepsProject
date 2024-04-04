from import_export import resources
from .models import *

class StudentResource(resources.ModelResource):
    class Meta:
        model = User
class QuestionResource(resources.ModelResource):
    class Meta: 
        model = Question
        exclude = ('id',)
