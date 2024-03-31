from django.shortcuts import render, redirect
from .forms import *
from django.shortcuts import render
from .models import *
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import User
import string
import os





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define a custom test function to check if the user is a department or other
def is_department(user):
    return user.is_authenticated and user.is_department
def is_student(user):
    return user.is_authenticated and user.is_student
def is_admin(user):
    return user.is_authenticated and user.is_staff and user.is_superuser

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Login View
def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                if user.is_staff and user.is_superuser:
                    return redirect('home')
                elif user.is_department:
                    return redirect('department_home')
                elif user.is_student:
                    return redirect('student_home')
            else:
                msg = 'Invalid email or password. Please try again.'

    return render(request, 'login.html', {'form': form, 'msg': msg})
#/Login View/ 




########################### Admin Views ###############################
#Admin Home
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def home(request):
    # Calculate the total number of departments
    total_departments = User.objects.filter(is_department=True).count()
    total_students = User.objects.filter(is_student=True).count()
    exams = Exam.objects.all().count()
    context = {
        'total_departments': total_departments,
        'total_students':total_students,
        'exams':exams,
    }
    return render(request, 'admin_template/dashboard.html', context)

 
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def feedback(request):
     return render(request, 'admin_template/feedback.html')

# def admin_register(request):
#     msg = None
#     if request.method == 'POST':
#         form = AdminRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_admin = True  # Set is_admin to True
#             user.save()
#             msg = 'Admin user created'
#             return redirect('login_view')
#         else:
#             msg = 'Form is not valid'
#     else:
#         form = AdminRegistrationForm()
#     return render(request, 'register_admin.html', {'form': form, 'msg': msg})
# Admin Add Department Form
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def add_department(request):
    success_msg = None
    error_msg = None
    
    if request.method == 'POST':
        form = DepartmentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_department = True  # Set is_department to True
            user.save()
            success_msg = 'Department added successfully!'
        else:
            error_msg = 'Form is not valid'
    else:
        form = DepartmentRegistrationForm()
    
    return render(request, 'admin_template/add_department.html', {
        'form': form,
        'success_msg': success_msg,
        'error_msg': error_msg
    })

#Admin View Department List
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def view_department(request):
    # Retrieve all registered departments with necessary fields, including username
    departments = User.objects.filter(is_department=True).values('username', 'department_name', 'email', 'college', 'phone')
    return render(request, 'admin_template/view_department.html', {'departments': departments})

#Admin Delete Department
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def delete_department(request, email):
    try:
        department = User.objects.get(email=email, is_department=True)
        department.delete()
    except User.DoesNotExist:
        # Handle the case where the department doesn't exist
        pass
    # Redirect to a view where you want to display the updated list of departments
    return redirect('view_department')
###########################/Admin Views/###############################






################ Department Views #####################
# Department Home Page
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def department_home(request):
    department_name = request.user.username
    department_username = request.user.username

    # Count the number of feedbacks
    feedbacks_count = Feedback.objects.filter(user__department_name=department_username).count()

    # Count the number of questions
    questions_count = Question.objects.filter(exam__department_name=department_username).select_related('exam').count()

    # Count the total number of students
    total_students = User.objects.filter(is_student=True, department_name=department_username).count()

    # Count the number of exams
    exams_count = Exam.objects.filter(department_name=department_name).count()

    # Pass the counts to the template
    context = {
        'total_students': total_students,
        'questions_count': questions_count,
        'exams_count': exams_count,
        'feedbacks_count': feedbacks_count,
    }

    return render(request, 'department_template/dashboard.html', context)

from django.contrib import messages

@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_student(request):
    success_msg = None
    error_msg = None
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, department_name=request.user.username)
        if form.is_valid():
            try:
                user = form.save()
                success_msg = 'Student added successfully!'
            except Exception as e:
                error_msg = f'An error occurred: {str(e)}'
        else:
            error_msg = 'Form is not valid'
    else:
        form = StudentRegistrationForm()

    return render(request, 'department_template/add_student.html', {
        'form': form,
        'success_msg': success_msg,
        'error_msg': error_msg
    })

    
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def view_student(request):
    # Retrieve the department name of the logged-in user
    department_name = request.user.username
    
    # Retrieve all registered students belonging to the department along with their full names
    students = User.objects.filter(is_student=True, department_name=department_name).values('username', 'first_name', 'last_name', 'email', 'sex', 'phone')

    # Fetch the total count of students belonging to the department
    total_students = students.count()
    for student in students:
        if student['sex'] == 'M':
            student['sex'] = 'Male'
        elif student['sex'] == 'F':
            student['sex'] = 'Female'
    # Pass the list of students and total count to the template
    context = {'students': students, 'total_students': total_students}

    return render(request, 'department_template/view_student.html', context)
from django.contrib import messages
from django.shortcuts import redirect, render

@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def delete_student(request, username):
    try:
        student = User.objects.get(username=username, is_student=True, department_name=request.user.username)
        student.delete()
        messages.success(request, 'Student deleted successfully!')
    except User.DoesNotExist:
        messages.error(request, 'Student not found or you do not have permission to delete.')

    return redirect('view_student')

def update_student(request, username):
    if request.method == 'POST':
        student = get_object_or_404(User, username=username, is_student=True, department_name=request.user.username)
        
        # Update fields based on form input
        student.first_name = request.POST.get('first_name')
       
        student.email = request.POST.get('email')
        student.sex = request.POST.get('sex')
        student.phone = request.POST.get('phone')
        # Add more fields as needed
        
        student.save()
        
        messages.success(request, 'Student updated successfully!')
        return redirect('view_student')  # Redirect to the view_student page after successful update
    else:
        return redirect('view_student') 


# views.py
from .forms import QuestionForm, ChoiceFormSet

@login_required(login_url='login_view')
# @user_passes_test(is_department, login_url='NoPage')
def add_question(request):
    success_msg = None
    error_msg = None

    department_username = request.user.username

    if request.method == 'POST':
        form = QuestionForm(request.POST, department_username=department_username)
        formset = ChoiceFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            success_msg = 'Question added successfully!'
        else:
            error_msg = 'Form is not valid'
            print("Form errors outside if:", form.errors, formset.errors)
    else:
        form = QuestionForm(department_username=department_username)
        formset = ChoiceFormSet(instance=form.instance)

    return render(request, 'department_template/add_question.html', {
        'form': form,
        'formset': formset,
        'success_msg': success_msg,
        'error_msg': error_msg
    })





######################/Department Views/#########################



def manage_questions(request):
    department_username = request.user.username
    questions = Question.objects.filter(exam__department_name=department_username).select_related('exam').all()
    return render(request, 'department_template/manage_question.html', {'questions': questions})
def update_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('manage_questions')
        else:
            messages.error(request, 'Error updating question. Please check the form.')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'department_template/manage_question.html', {'form': form, 'question': question})



def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('manage_questions')
    
    return redirect('manage_questions')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Exam

from django.db.models import Count

@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def manage_exam(request):
    # Retrieve the department name of the logged-in user
    department_name = request.user.username

    # Retrieve exams added by the department along with the number of questions for each exam
    exams = Exam.objects.filter(department_name=department_name).annotate(num_questions=Count('question'))

    if request.method == 'POST':
        activate_exam_id = request.POST.get('activate_exam_id')
        deactivate_exam_id = request.POST.get('deactivate_exam_id')

        if activate_exam_id:
            # Activate the exam
            try:
                exam = Exam.objects.get(pk=activate_exam_id)
                exam.is_active = True
                exam.save()
                messages.success(request, f'Exam {exam.name} has been activated successfully.')
            except Exam.DoesNotExist:
                messages.error(request, 'Exam not found.')

        elif deactivate_exam_id:
            # Deactivate the exam
            try:
                exam = Exam.objects.get(pk=deactivate_exam_id)
                exam.is_active = False
                exam.save()
                messages.success(request, f'Exam {exam.name} has been deactivated successfully.')
            except Exam.DoesNotExist:
                messages.error(request, 'Exam not found.')

    return render(request, 'department_template/manage_exam.html', {'exams': exams})



@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_exam(request):
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        form = ExamForm(request.POST, department_name=request.user.username)
        if form.is_valid():
            exam = form.save(commit=False)
            
            
            exam.save()
            
            messages.success(request, 'Exam Added successfully!')
            # Redirect to the manage_exam view after adding the exam
            return redirect('add_exam')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = ExamForm()

    return render(request, 'department_template/add_exam.html', {
        'form': form,
        'success_msg': success_msg,
        'error_msg': error_msg
    })


def update_exam(request, exam_id):
    if request.method == 'POST':
        exam = Exam.objects.get(pk=exam_id)
        # Update exam fields based on form input
        exam.name = request.POST.get('exam_name')
        exam.timer = request.POST.get('exam_duration')
        exam.exam_code = request.POST.get('exam_code')
        # Add more fields as needed
        exam.save()
        messages.success(request, 'Exam updated successfully!')
        return redirect('manage_exam')  # Redirect to the manage_exam page after successful update
    else:
        return redirect('manage_exam')  
    

def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted successfully!')
    return redirect('manage_exam')
    
    
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def feedback_management(request):
    # Retrieve the logged-in department's username
    department_username = request.user.username

    # Retrieve feedback from students of the logged-in department
    student_feedback = Feedback.objects.filter(user__is_student=True, user__department_name=department_username)

    # Pass the list of feedback to the template
    context = {'student_feedback': student_feedback}

    return render(request, 'department_template/view_feedback.html', context)




@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def manage_courses(request):
    # Retrieve the department name of the logged-in user
    department_name = request.user.username

    # Retrieve courses added by the department
    courses = Course.objects.filter(department_name=department_name)

    # Remove "files/resources/" from the resource path for each course
    for course in courses:
        file_name = os.path.basename(course.resource.name)
        course.resource = file_name

    if request.method == 'POST':
        activate_course_id = request.POST.get('activate_course_id')
        deactivate_course_id = request.POST.get('deactivate_course_id')

        if activate_course_id:
            # Activate the course
            try:
                course = Course.objects.get(pk=activate_course_id)
                course.is_active = True
                course.save()
                messages.success(request, f'Course {course.title} has been activated successfully.')
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')

        elif deactivate_course_id:
            # Deactivate the course
            try:
                course = Course.objects.get(pk=deactivate_course_id)
                course.is_active = False
                course.save()
                messages.success(request, f'Course {course.title} has been deactivated successfully.')
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')

    return render(request, 'department_template/manage_courses.html', {'courses': courses})
from django.http import HttpResponseNotFound
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def delete_course(request, course_id):
    if request.method == 'POST':
        try:
            course = Course.objects.get(pk=course_id)
            course.delete()
            messages.success(request, f'Course {course.title} deleted successfully.')
            return redirect('manage_courses')  # Replace 'manage_courses' with the URL name of your manage view for courses
        except Course.DoesNotExist:
            return HttpResponseNotFound('<h1>Course not found</h1>')
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')


def manage_tutorials(request):
    department_name = request.user.username
    courses = Course.objects.filter(department_name=department_name)
    tutorials = Tutorial.objects.filter(course__in=courses)
    return render(request, 'department_template/manage_tutorials.html', {'tutorials': tutorials})



from django.contrib import messages
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_course(request):
    success_msg = None
    error_msg = None

    department_name = request.user.username  # Verify the department name is correctly set
   
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, department_name=department_name)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course deleted successfully!')
            return redirect('add_course')
        else:
            messages.error(request, 'Form is not valid')
    else:
        form = CourseForm(department_name=department_name)

    return render(request, 'department_template/add_course.html', {
        'form': form
    })


# views.py
from django.shortcuts import render, redirect
from .forms import TutorialForm
# views.py
from django.shortcuts import render, redirect
from .forms import TutorialForm
from .models import Course


@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_tutorial(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_tutorial')  # Redirect to the same page after adding a tutorial
    else:
        department_name = request.user.username  # Get department name from user
        courses = Course.objects.filter(department_name=department_name)  # Filter courses by department
        # Pass the department to the form
        form = TutorialForm(department=department_name)
        
    return render(request, 'department_template/add_tutorial.html', {
        'form': form,
    })

# def edit_course(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     if request.method == 'POST':
#         course.title = request.POST.get('title')
#         course.description = request.POST.get('description')
#         course.resource = request.FILES.get('resource') or course.resource
#         course.thumbnail = request.FILES.get('thumbnail') or course.thumbnail
#         course.is_active = request.POST.get('is_active')
#         course.save()
#         return redirect('manage_courses')
#     return render(request, 'department_template/edit_course.html', {'course': course})

# def delete_course(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     if request.method == 'POST':
#         course.delete()
#         return redirect('manage_courses')
#     return render(request, 'department_template/delete_course.html', {'course': course})


####################### Student Views ############################
#Student Home Page
@login_required(login_url='login_view')
@user_passes_test(is_student, login_url='NoPage')
def student_home(request):
    # Retrieve the first name of the current user
    first_name = request.user.first_name
    
    department_name = request.user.department_name
    # Retrieve all active courses from the database
    courses = Course.objects.filter(department_name=department_name, is_active=True)
    
    return render(request, 'student_template/student_home.html', {'first_name': first_name, 'courses': courses})


@login_required(login_url='login_view')
@user_passes_test(lambda user: user.is_student, login_url='NoPage')
def view_exams(request):
    # Retrieve the logged-in student's department name
    department_name = request.user.department_name

    # Filter exams based on the department name and only include activated exams
    exams = Exam.objects.filter(department_name=department_name, is_active=True)

    return render(request, 'student_template/view_exams.html', {'exams': exams})



from django.shortcuts import render
from django.db.models import Prefetch
from .models import Exam, Question, Choice

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question  # Import your Exam and Question models

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question  # Import your Exam and Question models

def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Check if the user has entered the correct exam code
    entered_exam_code = request.session.get(f'exam_code_{exam_id}')
    if not entered_exam_code or entered_exam_code != exam.exam_code:
        messages.error(request, 'Please enter the correct exam code to access the exam details.')
        return redirect('enter_exam_code', exam_id=exam_id)

    # Clear the session variable for the entered exam code
    del request.session[f'exam_code_{exam_id}']

    # Use prefetch_related to fetch choices along with questions in a single query
    questions = Question.objects.filter(exam=exam).prefetch_related('choice_set')

    context = {
        'exam': exam,
        'questions': questions,
    }

    return render(request, 'student_template/exam_detail.html', context)




# views.py
from django.shortcuts import render, redirect
from .models import Result, Exam, Question, Choice

def submit_exam(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    questions = Question.objects.filter(exam=exam)

    if request.method == 'POST':
        # Calculate the number of correct answers
        correct_answers = 0
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}', None)
            if selected_choice_id:
                selected_choice = Choice.objects.get(pk=selected_choice_id)
                if selected_choice.is_correct:
                    correct_answers += 1

        # Store the result in the database
        result = Result.objects.create(student=request.user, exam=exam, score=correct_answers)

        return render(request, 'student_template/exam_submitted.html', {
            'correct_answers': correct_answers,
            'total_questions': len(questions),
            'result': result,
        })

    return redirect('view_exams')  # Redirect to the view_exams page if it's not a POST request

from django.shortcuts import render, get_object_or_404

# views.py
# views.py
from django.shortcuts import render, redirect
from .models import Result, Exam, Question, Choice

def result(request, result_id):
    result = get_object_or_404(Result, pk=result_id)
    
    # Get questions and choices for the result
    questions = Question.objects.filter(exam=result.exam).prefetch_related('choice_set')
    questions_with_choices = []

    for question in questions:
        # Find the correct choice for each question
        correct_choice = question.choice_set.filter(is_correct=True).first()

        # Add the correct choice to the question object
        question.correct_choice = correct_choice
        questions_with_choices.append(question)

    return render(request, 'student_template/result.html', {
        'result': result,
        'questions_with_choices': questions_with_choices,
    })



# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Exam

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Exam

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Exam  # Import your Exam model

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Exam  # Import your Exam model

from django.shortcuts import get_object_or_404

@login_required(login_url='login_view')
def enter_exam_code(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Retrieve the number of questions for the exam
    num_questions = exam.question_set.count()

    if request.method == 'POST':
        entered_exam_code = request.POST.get('exam_code', '').strip()

        if entered_exam_code:
            if entered_exam_code == exam.exam_code:
                # Store the entered exam code in the session
                request.session[f'exam_code_{exam_id}'] = entered_exam_code
                # Redirect to the exam details page if the entered code is correct
                return redirect('exam_detail', exam_id=exam_id)
            else:
                messages.error(request, 'Invalid exam code. Please try again.')
        else:
            messages.error(request, 'Please enter a valid exam code.')

    return render(request, 'student_template/enter_exam_code.html', {'exam': exam, 'num_questions': num_questions})


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm

from django.contrib import messages
@login_required(login_url='login_view')

def submit_feedback(request):
    user = request.user
    success_msg = None

    # Check if the user already submitted feedback
    existing_feedback = Feedback.objects.filter(user=user).first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        
        if form.is_valid():
            # Save the feedback with user's information
            feedback = form.save(commit=False)
            feedback.user = user
            feedback.username = user.username
            feedback.email = user.email
            feedback.save()

            # Set success message using Django messages framework
            messages.success(request, 'Feedback submitted successfully.')
            success_msg = 'Feedback submitted successfully.'  # Set success_msg variable

            return redirect('submit_feedback')  # Redirect to the feedback page
    else:
        form = FeedbackForm()

    return render(request, 'student_template/feedback.html', {'form': form, 'success_msg': success_msg})



# views.py
from django.shortcuts import render
from .models import Course
from django.shortcuts import render, get_object_or_404
from .models import Course, Tutorial

def tutorial_page(request, course_id):
    # Retrieve the course object based on the course ID
    course = Course.objects.get(pk=course_id)
    # Retrieve all tutorials associated with the course
    tutorials = Tutorial.objects.filter(course=course)
    # Pass the course and tutorials to the template
    return render(request, 'student_template/tutorial_page.html', {'course': course, 'tutorials': tutorials})

    
####################/Student Views/###############################




def logout_view(request):
    logout(request)
    return redirect('login_view')

def NoPage(request):
    return render(request,'404.html')