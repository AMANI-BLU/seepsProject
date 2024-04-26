from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class User(AbstractUser):
    is_admin = models.BooleanField('Is admin', default=False)
    is_department = models.BooleanField('Is department', default=False)
    is_student = models.BooleanField('Is student', default=False)
    is_instructor = models.BooleanField('Is instructor', default=False)
    college = models.CharField(max_length=255, blank=True, null=True)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True) 
    sex = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')),blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


class Exam(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    name = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    timer = models.PositiveIntegerField()
    exam_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=False)
    attempts_allowed = models.IntegerField(default=3)  # Add attempts allowed field
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='intermediate')
    submitted_by = models.ManyToManyField(User, through='ExamSubmission', related_name='submitted_exams')

    def __str__(self):
        return self.name

class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'user')  # Ensure uniqueness of exam submission per user



class Attempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt by {self.student.username} on {self.exam.name}"
    

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    content = models.TextField()
    answer_description = models.TextField(blank=True, null=True)

  
    def __str__(self):
        return f"{self.exam.name}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice for {self.question}"



class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student.username}'s Result for {self.exam.name}"


 

class Course(models.Model):
    title = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    resource = models.FileField(upload_to='files/resources/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='files/thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    prerequisites = models.TextField()  # Added prerequisites field to Course model
    learning_outcomes = models.TextField()  # Added learning_outcomes field to Course model

    def __str__(self):
        return self.title

class Tutorial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    tutorial_url = models.CharField(max_length=100)  # New field for tutorial URL

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title



class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.user.username} at {self.created_at}'



class Resource(models.Model):
    file = models.FileField(upload_to='resources/')
    description = models.TextField()
    department_name = models.CharField(max_length=255, blank=True, null=True)
    added_by = models.CharField(max_length=255, blank=True, null=True)  

    def __str__(self):
        return self.name
