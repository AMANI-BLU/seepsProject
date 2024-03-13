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
       
    # forms.py
    
    
    
    
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
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder":"username"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder":"password"
            }
        )
    )

class AdminRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class DepartmentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your username"
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
        fields = ('username', 'email', 'college', 'phone', 'password1', 'password2')
    
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


class StudentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your username"
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
            "class": "form-conztrol",
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
        fields = ('username', 'email', 'college', 'phone', 'password1', 'password2')
    
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


# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your username"
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
        fields = ('username', 'email', 'college', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        self.department_username = kwargs.pop('department_username', None)
        super(StudentRegistrationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(StudentRegistrationForm, self).save(commit=False)
        user.is_student = True
        user.department_name = self.department_username  # Set the department for the student
        if commit:
            user.save()
        return user
