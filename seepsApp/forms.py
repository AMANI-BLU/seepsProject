#forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory 
from .models import User
from django import forms
from .models import Exam
# forms.py
from django import forms
from .models import *

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'timer','exam_code']

    def __init__(self, *args, **kwargs):
        self.department_name = kwargs.pop('department_name', None)
        super(ExamForm, self).__init__(*args, **kwargs)

        # Add attributes to other form fields if needed
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter exam name',
        })

        self.fields['timer'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Timer in minutes',
            'type': 'time',  # This is the attribute for the time picker
        })
        self.fields['exam_code'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter exam code',
        })

    def save(self, commit=True):
        exam = super(ExamForm, self).save(commit=False)
        exam.department_name = self.department_name  # Set the department_name for the exam
        if commit:
            exam.save()
        return exam

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['feedback_text'].widget.attrs.update({
            'class': 'form-control text-muted',
            'placeholder': 'Enter your feedback here..',
             'rows': '5',
        })
        self.fields['feedback_text'].label = ''
        self.fields['feedback_text'].label_suffix = ''  # Remove default ':' after label
       
from django import forms
from .models import Course
from django import forms
from .models import Course

from django import forms
from .models import Course



from django import forms
from .models import Tutorial

class TutorialForm(forms.ModelForm):
    class Meta:
        model = Tutorial
        fields = ['course', 'title', 'tutorial_url']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tutorial Title'}),
            'tutorial_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tutorial URL'}),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super(TutorialForm, self).__init__(*args, **kwargs)
        if department:
            # Filter the queryset based on the department
            self.fields['course'].queryset = Course.objects.filter(department_name=department)

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        course = cleaned_data.get('course')

        if not title:
            raise forms.ValidationError("Tutorial title cannot be empty.")
        if not course:
            raise forms.ValidationError("Please select a course.")

        return cleaned_data

    def save(self, commit=True):
        tutorial = super(TutorialForm, self).save(commit=False)
        if commit:
            tutorial.save()
        return tutorial



from django import forms
from .models import Course
from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'department_name', 'description', 'resource', 'thumbnail', 'is_active', 'prerequisites', 'learning_outcomes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': '5'}),
            'resource': forms.FileInput(attrs={'class': 'form-control-file'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prerequisites': forms.Textarea(attrs={ 'class': 'form-control','id':'summernote', 'placeholder': 'Enter Question here..',}),
            'learning_outcomes': forms.Textarea(attrs={ 'class': 'form-control','id':'summernotee',}),
            'department_name': forms.HiddenInput(),  # Hidden field for department
        }

    def __init__(self, *args, **kwargs):
        self.department_name = kwargs.pop('department_name', None)
        print("Department Name:", self.department_name)  # Debug print
        super(CourseForm, self).__init__(*args, **kwargs)
        if self.department_name:
            self.fields['department_name'].initial = self.department_name

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        thumbnail = cleaned_data.get('thumbnail')

        # Custom validation for title not null
        if not title:
            raise forms.ValidationError("Title cannot be empty.")

        # Custom validation for thumbnail not null
        if not thumbnail:
            raise forms.ValidationError("Thumbnail is required.")

        return cleaned_data

    def save(self, commit=True):
        course = super(CourseForm, self).save(commit=False)
        course.department_name = self.department_name
        if commit:
            course.save()
        return course

from django import forms
from django.forms.models import inlineformset_factory
from .models import Question, Choice, Exam

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
             
            'text': forms.TextInput(attrs={'class':'form-control','placeholder':'enter choice here..'})
        }

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, can_delete=False, extra=4)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam', 'content']

    # Use formset attribute instead of choices
    choices = ChoiceFormSet()

    def __init__(self, *args, **kwargs):
        department_username = kwargs.pop('department_username', None)
        super(QuestionForm, self).__init__(*args, **kwargs)
        
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'id':'summernote',
            'placeholder': 'Enter Question here..',
        })
        self.fields['exam'].widget.attrs.update({
            'class': 'form-control',
           
        })

        if department_username:
            # If department_username is provided, this is a department adding a question
            self.fields['exam'].queryset = Exam.objects.filter(department_name=department_username)
        else:
            # If department_username is not provided, this is an admin adding a question
            self.fields['exam'].queryset = Exam.objects.all()


    # def __init__(self, department_username, *args, **kwargs):
    #     super(QuestionForm, self).__init__(*args, **kwargs)
    #     # Limit available exams to those belonging to the department
    #     self.fields['exam'].queryset = Exam.objects.filter(department_name=department_username)



# No need to override __init__, is_valid, or save methods for basic Django admin usage

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password"
            }
        )
    )


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class DepartmentRegistrationForm(UserCreationForm):
    department_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter department name"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email"
        })
    )
    college = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your college"
        })
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your phone number"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        })
    )

    class Meta:
        model = User
        fields = ('department_name', 'email', 'college', 'phone', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only numeric digits.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username()
        if commit:
            user.save()
        return user

    def generate_username(self):
        department_name = self.cleaned_data.get('department_name')
        email = self.cleaned_data.get('email')
        # Here you can generate a unique username based on department name and email
        # For example, you can concatenate them and use a hashing algorithm to ensure uniqueness
        # Here's a simple example:
        username = f"{department_name}_{email}".replace('@', '_').replace('.', '_')
        return username




from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User



class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your full name"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email"
        })
    )
    sex_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    sex = forms.ChoiceField(
        choices=sex_choices,
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )
    
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your phone number"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password"
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        })
    )

    def __init__(self, *args, **kwargs):
        self.department_name = kwargs.pop('department_name', None)
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'sex',  'phone', 'password1', 'password2')

    def generate_username(self):
        first_name = self.cleaned_data.get('first_name')
        email = self.cleaned_data.get('email')
        username = f"{first_name}_{email}".replace('@', '_').replace('.', '_')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.username = self.generate_username()
        user.department_name = self.department_name
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
