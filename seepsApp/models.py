from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_department = models.BooleanField('Is department', default=False)
    is_student = models.BooleanField('Is student', default=False)
    college = models.CharField(max_length=255, blank=True, null=True)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
class Exam(models.Model):
    name = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    timer = models.PositiveIntegerField()
    exam_code = models.CharField(max_length=10)  # Add this line for the exam code
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
# models.py
# models.py
class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    content = models.TextField()
  
    def __str__(self):
        return f"{self.exam.name}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice for {self.question}"


# models.py
class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student.username}'s Result for {self.exam.name}"


 
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    resource = models.FileField(upload_to='files/resources/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='files/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.user.username} at {self.created_at}'
    