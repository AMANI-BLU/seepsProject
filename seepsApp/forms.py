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
# forms.py

from django import forms
from .models import Exam

class ExamForm(forms.ModelForm):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    attempts_allowed = forms.IntegerField(label='Attempts Allowed', min_value=1)
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES)

    class Meta:
        model = Exam
        fields = ['name', 'timer', 'exam_code', 'attempts_allowed', 'difficulty']

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

        self.fields['attempts_allowed'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter number of attempts allowed',
        })

        self.fields['difficulty'].widget.attrs.update({
            'class': 'form-control',
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
from django import forms
from .models import Tutorial, Course

from django import forms
from django.core.exceptions import ValidationError
from .models import Tutorial, Course


class TutorialForm(forms.ModelForm):
    order = forms.IntegerField(label='Order', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Tutorial
        fields = ['course', 'title', 'tutorial_url', 'order']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tutorial Title'}),
            'tutorial_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tutorial URL'}),
        }

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super(TutorialForm, self).__init__(*args, **kwargs)
        if department:
            self.fields['course'].queryset = Course.objects.filter(department_name=department)

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')

        if not course:
            raise forms.ValidationError("Please select a course.")
        
        return cleaned_data

    def clean_order(self):
        order = self.cleaned_data.get('order')
        course = self.cleaned_data.get('course')

        if not course:
            return order

        if Tutorial.objects.filter(course=course, order=order).exists():
            raise forms.ValidationError("A tutorial with the same order already exists for this course.")

        return order

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
   

from django.forms.models import inlineformset_factory
from .models import Question, Choice, Exam
from django.core.exceptions import ValidationError


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        labels = {
            'text': 'Choice',
        }
        widgets = {
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input mt-2 ml-2'}),
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter choice here..'})
        }

# Custom formset class to dynamically set extra forms and validate minimum number of choices
class BaseChoiceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra', 4)
        super().__init__(*args, **kwargs)
        self.extra = extra

    def clean(self):
        super().clean()
        if len(self.forms) < 2:
            raise ValidationError('You must enter at least two choices.')

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, formset=BaseChoiceFormSet, can_delete=False)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam', 'content', 'weight','answer_description']  # Include 'weight' field
        labels = {
            'content': 'Question',
        }
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control summernote', 'placeholder': 'Enter Question here..'}),
            'answer_description': forms.Textarea(attrs={'class': 'form-control summernote', 'placeholder': 'Enter answer description here..'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Question weight'}),
        }

    def __init__(self, *args, **kwargs):
        department_username = kwargs.pop('department_username', None)
        super(QuestionForm, self).__init__(*args, **kwargs)
        
        if department_username:
            queryset = Exam.objects.filter(department_name=department_username)
        else:
            queryset = Exam.objects.all()

        choices = [(exam.id, f"{exam.name} ({exam.difficulty})") for exam in queryset]
        self.fields['exam'].choices = choices
        self.fields['content'].widget.attrs.update({
            'class': 'form-control summernote',
            'placeholder': 'Enter Question here..',
        })
        self.fields['answer_description'].widget.attrs.update({
            'class': 'form-control summernote',
            'placeholder': 'Enter answer description here..',
        })
    # Include the choice formset
    choices = ChoiceFormSet()


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
import string
import random
import re

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
        }),
        required=False  # Set to False to avoid validation errors
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        }),
        required=False  # Set to False to avoid validation errors
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
        
        # Define the regular expression pattern
        pattern = r'^(\+2519\d{8}|09\d{8}|07\d{8}|2517\d{8})$'
        
        # Check if the phone matches the pattern
        if not re.match(pattern, phone):
            raise forms.ValidationError('Phone number must be in the format +2519xxxxxxxx, 09xxxxxxxx, 07xxxxxxxx, or +2517xxxxxxxx.')
        
        return phone
    
    def clean_department_name(self):
        department_name = self.cleaned_data.get('department_name')
        if not re.match(r'^[a-zA-Z ]+$', department_name):
            raise forms.ValidationError("Department name must contain only alphabetic characters and spaces")
        return department_name
    
    
    def clean_college(self):
        college = self.cleaned_data.get('college')
        if not re.match(r'^[a-zA-Z ]+$', college):
            raise forms.ValidationError("College name must contain only alphabetic characters and spaces")
        return college

   

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.generate_username()
        password = self.generate_password()  # Generate a random password
        user.set_password(password)  # Set the password
        if commit:
            user.save()
        return user

    def generate_username(self):
        department_name = self.cleaned_data.get('department_name')
        college = self.cleaned_data.get('college')

        # Get the first character of department_name and college
        initials = department_name[0].upper() + college[0].upper()

        # Add random numbers for uniqueness
        username = f"{initials}_{random.randint(100, 999)}"
        return username

    def generate_password(self):
        length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

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
        ('Male', 'Male'),
        ('Female', 'Female')
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
            "placeholder": "Enter your phone number",
  
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password"
        }),
        required=False  # Set to False to avoid validation errors
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        }),
        required=False  # Set to False to avoid validation errors
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

    def generate_password(self):
        length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z ]+$', first_name):
            raise forms.ValidationError("First name must contain only alphabetic characters and spaces")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        # Define the regular expression pattern
        pattern = r'^(\+2519\d{8}|09\d{8}|07\d{8}|\+2517\d{8})$'
        
        # Check if the phone matches the pattern
        if not re.match(pattern, phone):
            raise forms.ValidationError('Phone number must be in the format +2519xxxxxxxx, 09xxxxxxxx, 07xxxxxxxx, or +2517xxxxxxxx.')
        
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.username = self.generate_username()
        user.department_name = self.department_name
        password = self.generate_password()  # Generate a random password
        user.set_password(password)  # Set the password
        if commit:
            user.save()
        return user
    
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'department_name', 'email', 'phone', 'sex', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control'
            })
        if self.instance.is_superuser:
            self.fields['department_name'].required = False
            if 'department_name' in self.fields:
                del self.fields['department_name']
            self.fields['username'] = forms.CharField(max_length=150, required=True)
        elif self.instance.is_student:
            self.fields['department_name'].required = True
        elif self.instance.is_instructor:
            self.fields['department_name'].required = False
            if 'department_name' in self.fields:
                del self.fields['department_name']

    def save(self, commit=True):
        user = super(ProfileUpdateForm, self).save(commit=False)
        if hasattr(user, 'username'):
            user.username = self.cleaned_data.get('username', user.username)
        if commit:
            user.save()
        return user


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['description', 'file']
        
from django import forms
from .models import Exam

class UploadPdfForm(forms.Form):
    pdf_file = forms.FileField(label='Upload PDF', help_text='Select a PDF file')
    exam = forms.ChoiceField(choices=(), label='Select Exam', widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, department_queryset=None, **kwargs):
        super(UploadPdfForm, self).__init__(*args, **kwargs)
        
        if department_queryset:
            choices = [(exam.id, f"{exam.name} ({exam.difficulty})") for exam in department_queryset]
            self.fields['exam'].choices = choices


# forms.py


class EditQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam', 'content', 'answer_description']
        labels = {
            'content': 'Question',
        }
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control','id': 'summernote', 'placeholder': 'Enter Question here..'}),
            'answer_description': forms.Textarea(attrs={'class': 'form-control','id': 'summernote', 'placeholder': 'Enter answer description here..'}),
        }

    choices = ChoiceFormSet()

    def __init__(self, *args, **kwargs):
        department_username = kwargs.pop('department_username', None)
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        
        if department_username:
            # Filter exams based on the department username
            queryset = Exam.objects.filter(department_name=department_username)
        else:
            queryset = Exam.objects.all()

        choices = [(exam.id, f"{exam.name} ({exam.difficulty})") for exam in queryset]
        self.fields['exam'].choices = choices
        self.fields['content'].widget.attrs.update({
            'class': 'form-control summernote',
            'placeholder': 'Enter Question here..',
        })
        self.fields['answer_description'].widget.attrs.update({
            'class': 'form-control summernote',
            'placeholder': 'Enter answer description here..',
        })
EditChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=False)



# Instructor Registration Form
class InstructorRegistrationForm(UserCreationForm):
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
        ('Male', 'Male'),
        ('Female', 'Female')
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
        }),
        required=False  # Set to False to avoid validation errors
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        }),
        required=False  # Set to False to avoid validation errors
    )

    def __init__(self, *args, **kwargs):
        self.department_name = kwargs.pop('department_name', None)
        super(InstructorRegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('first_name', 'email', 'sex', 'phone', 'password1', 'password2')

    def generate_username(self):
        first_name = self.cleaned_data.get('first_name')
        email = self.cleaned_data.get('email')
        username = f"{first_name}_{email}".replace('@', '_').replace('.', '_')
        return username

        
    def generate_password(self):
        length = 12
        characters = string.ascii_letters + string.digits
        # Choose at most 2 special characters
        special_characters = string.punctuation
        if length > 2:
            special_characters = ''.join(random.sample(special_characters, min(2, len(special_characters))))
        password = ''.join(random.choice(characters) for _ in range(length - 2))  # Use 10 characters for letters and digits
        password += special_characters  # Append the chosen special characters
        password = ''.join(random.sample(password, len(password)))  # Shuffle the password
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z ]+$', first_name):
            raise forms.ValidationError("First name must contain only alphabetic characters and spaces")
        return first_name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Define the regular expression pattern
        pattern = r'^(\+2519\d{8}|09\d{8}|07\d{8}|\+2517\d{8})$'
        # Check if the phone matches the pattern
        if not re.match(pattern, phone):
            raise forms.ValidationError('Phone number must be in the format +2519xxxxxxxx, 09xxxxxxxx, 07xxxxxxxx, or +2517xxxxxxxx.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        user.username = self.generate_username()
        user.department_name = self.department_name
        password = self.generate_password()  # Generate a random password
        user.set_password(password)  # Set the password
        if commit:
            user.save()
        return user
    


class DashboardForm(forms.Form):
    text = forms.CharField(max_length=100, label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your search here'}))
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('This field cannot be empty.')
        return text
        
    

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter event title'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter event description'}),
        }

# forms.py



class CommunityQuestionForm(forms.ModelForm):
    class Meta:
        model = CommunityQuestion
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the title of your question'}),
            'body': forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 5, 'placeholder': 'Enter your question here'}),
        }

class CommunityAnswerForm(forms.ModelForm):
    class Meta:
        model = CommunityAnswer
        fields = ['body']

class CommunityCommentForm(forms.ModelForm):
    class Meta:
        model = CommunityComment
        fields = ['body']








class StudentSelfRegistrationForm(forms.ModelForm):
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
        ('Male', 'Male'),
        ('Female', 'Female')
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
            "placeholder": "Enter your phone number",
        })
    )
    department = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'email', 'sex', 'phone', 'department')

    def __init__(self, *args, **kwargs):
        departments = kwargs.pop('departments', [])
        super(StudentSelfRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['department'].choices = [(dept.id, dept.department_name) for dept in departments]
        print("Form initialized with departments")

    def generate_username(self):
        first_name = self.cleaned_data.get('first_name')
        email = self.cleaned_data.get('email')
        username = f"{first_name}_{email}".replace('@', '_').replace('.', '_')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            print(f"Email already exists: {email}")
            raise forms.ValidationError("Email already exists")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^(\+2519\d{8}|09\d{8}|07\d{8}|\+2517\d{8})$'
        if not re.match(pattern, phone):
            print(f"Invalid phone number: {phone}")
            raise forms.ValidationError('Phone number must be in the format +2519xxxxxxxx, 09xxxxxxxx, 07xxxxxxxx, or +2517xxxxxxxx.')
        return phone

    def generate_password(self):
        length = 12
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def save(self, commit=True):
        print("Saving user")
        user = super().save(commit=False)
        user.is_student = True
        user.username = self.generate_username()
        department_id = self.cleaned_data.get('department')
        if department_id:
            # Fetch the department's username and store it
            department = User.objects.get(id=department_id)
            user.department_name = department.username  # Store the department's username
        password = self.generate_password()  # Generate a random password
        print(f"Generated password: {password}")
        user.set_password(password)
        if commit:
            user.save()
        return user