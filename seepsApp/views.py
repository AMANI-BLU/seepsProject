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
def is_instructor(user):
    return user.is_authenticated and user.is_instructor

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
                    return redirect('department_home')  # Render a template informing the user to verify their account
                elif user.is_student:
                    return redirect('student_home')
                elif user.is_instructor:
                    return redirect('instructor_home')
            else:
                msg = 'Invalid email or password. Please try again.'

    return render(request, 'login.html', {'form': form, 'msg': msg})
#/Login View/ 



from django.db.models import Count

#Admin Home
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def home(request):
    # Calculate the total number of departments
    total_departments = User.objects.filter(is_department=True).count()
    total_students = User.objects.filter(is_student=True).count()
    exams = Exam.objects.all().count()
    feedbacks = Feedback.objects.all().count()

    # Fetch department distribution by college
    department_distribution = User.objects.filter(is_department=True).values('college').annotate(department_count=Count('college'))

    # Prepare data for the chart
    college_names = []
    department_counts = []
    for data in department_distribution:
        college_names.append(data['college'])
        department_counts.append(data['department_count'])

    context = {
        'total_departments': total_departments,
        'total_students': total_students,
        'exams': exams,
        'college_names': college_names,
        'department_counts': department_counts,
        'feedbacks':feedbacks
    }
    return render(request, 'admin_template/dashboard.html', context)


 
@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def feedback(request):
     student_feedback = Feedback.objects.all()
     return render(request, 'admin_template/feedback.html',{'student_feedback':student_feedback})

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
# File: views.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.hashers import make_password

@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='NoPage')
def add_department(request):
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        form = DepartmentRegistrationForm(request.POST)
        if form.is_valid():
            # Generate the password
            password = form.generate_password()

            # Create a user instance with the generated password
            user = form.save(commit=False)
            user.is_department = True  # Set is_department to True
            user.password = make_password(password)  # Hash the password
            user.save()

            success_msg = 'Department added successfully!'
            
            # Send email
            subject = 'Department Account Verification'
            html_message = render_to_string('email/department_account_email.html', {
                'user': user,
                'password': password,  # Pass the generated password to the email template
            })
            plain_message = strip_tags(html_message)  # Strip HTML tags for plain text message
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
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

def update_department(request, username):
    if request.method == 'POST':
        department_user = get_object_or_404(User, username=username, is_department=True,)
        
        # Update fields based on form input
        department_user.department_name = request.POST.get('department_name')
        department_user.email = request.POST.get('email')
        department_user.phone = request.POST.get('phone')
        department_user.college = request.POST.get('college')
        # Add more fields as needed
        
        department_user.save()
        
        messages.success(request, 'Department updated successfully!')
        return redirect('view_department')  # Redirect to the view_department page after successful update
    else:
        return redirect('view_department')
###########################/Admin Views/###############################





@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def department_home(request):
    department_name = request.user.username
    department_username = request.user.username
    instructors = User.objects.filter(department_name=department_name, is_instructor=True).count()
    # Fetching data for department dashboard
    students = User.objects.filter(is_student=True, department_name=department_name)
    feedbacks_count = Feedback.objects.filter(user__department_name=department_username).count()
    questions_count = Question.objects.filter(exam__department_name=department_username).select_related('exam').count()
    total_students = User.objects.filter(is_student=True, department_name=department_username).count()
    exams_count = Exam.objects.filter(department_name=department_name).count()
    male_count = sum(1 for student in students if student.sex == 'Male')
    female_count = sum(1 for student in students if student.sex == 'Female')

    # Fetching data for exam scores table
    aggregate_data = fetch_exam_scores_data(department_name)

    # Pass the counts and exam scores data to the template
    context = {
        'instructors':instructors,
        'total_students': total_students,
        'questions_count': questions_count,
        'exams_count': exams_count,
        'feedbacks_count': feedbacks_count,
        'male_count': male_count,
        'female_count': female_count,
        'exam_scores_data': aggregate_data,
        'passed_students_count': sum(data['passed_students_count'] for data in aggregate_data),
        'failed_students_count': sum(data['failed_students_count'] for data in aggregate_data),
    }

    return render(request, 'department_template/dashboard.html', context)



def fetch_exam_scores_data(department_name):
    # Subquery to count the number of questions for each exam
    num_questions_subquery = Subquery(
        Exam.objects.filter(id=OuterRef('exam')).annotate(
            num_questions=Count('question')
        ).values('num_questions')
    )
    
    # Aggregate exam scores for each exam in the department
    aggregate_data = Result.objects.filter(exam__department_name=department_name).values(
        'exam__name'
    ).annotate(
        num_students=Count('student', distinct=True),  # Count the number of distinct students for each exam
        average_score=Avg('score'),
        highest_score=Max('score'), 
        lowest_score=Min('score'),
        num_questions=num_questions_subquery,
    )

    # Process the aggregated data
    for data in aggregate_data:
        # Initialize counters for passed and failed students
        passed_students_count = 0
        failed_students_count = 0
        
        # Calculate the pass/fail threshold
        pass_fail_threshold = data['num_questions'] // 2
        
        # Check each student's score against the pass/fail threshold
        for result in Result.objects.filter(exam__name=data['exam__name']):
            if result.score >= pass_fail_threshold:
                passed_students_count += 1
            else:
                failed_students_count += 1
        
        # Add the counts to the data dictionary
        data['passed_students_count'] = passed_students_count
        data['failed_students_count'] = failed_students_count

    return aggregate_data

# views.py



from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to maintain the user's session
            messages.success(request, 'Your password was successfully updated!')
            if is_department(request.user):
                return redirect('department_home')
            elif is_student(request.user):
                return redirect('student_home')
            elif is_admin(request.user):
                return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})



from .forms import ProfileUpdateForm


def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')  # Redirect to profile page after successful update
        else:
            messages.error(request, 'Failed to update profile. Please correct the errors.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})




from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Feedback

@require_POST
def delete_feedback(request):
    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    # Add a success message
    messages.success(request, 'Feedback deleted successfully!')
    return redirect('feedback_management')  # Redirect to the feedback page after deletion

@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_student(request):
    success_msg = None
    error_msg = None
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, department_name=request.user.username)
        if form.is_valid():
            # Generate the password
            password = form.generate_password()

            try:
                user = form.save(commit=False)
                user.is_student = True
                user.set_password(password)  # Hash the password
                user.save()
                success_msg = 'Student registered successfully!'

                # Send email
                subject = 'Student Account Verification'
                html_message = render_to_string('email/student_account_email.html', {
                    'user': user,
                    'password': password,  # Pass the generated password to the email template
                    # 'login_url': 'http://127.0.0.1:8000/login/',  # Provide the login URL
                })
                plain_message = strip_tags(html_message)  # Strip HTML tags for plain text message
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = user.email
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
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
    students = User.objects.filter(is_student=True, department_name=department_name)
    
    # Initialize counters for male and female students
    male_count = 0
    female_count = 0

    # Iterate through the students queryset to count male and female students
    for student in students:
        if student.sex == 'male':  # Corrected: accessing sex directly from student object
            male_count += 1
        elif student.sex == 'female':  # Corrected: accessing sex directly from student object
            female_count += 1

    # Fetch the total count of students belonging to the department
    total_students = students.count()

    # Pass the list of students, total count, and counts of male and female students to the template
    context = {
        'students': students,
        'total_students': total_students,
        'male_count': male_count,
        'female_count': female_count,
    }

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



@login_required(login_url='login_view')
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
            # error_msg = 'Form is not valid'
            print("Form errors outside if:", form.errors, formset.errors)
    else:
        form = QuestionForm(department_username=department_username)
        # Determine the number of extra forms based on the number of additional choice fields submitted
        num_extra = len(request.POST.getlist('form-0-text')) - 1 if request.POST.get('form-0-text') else 2
        formset = ChoiceFormSet(instance=Question(), extra=num_extra)

    return render(request, 'department_template/add_question.html', {
        'form': form,
        'formset': formset,
        'success_msg': success_msg,
        'error_msg': error_msg
    })

######################/Department Views/#########################


def add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.department_name = request.user.username  # Assuming department_name is associated with the user
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('manage_resources')
    else:
        form = ResourceForm()
    return render(request, 'department_template/add_resource.html', {'form': form})

def manage_resources(request):
    # Get the department username of the logged-in user
    department_username = request.user.username
    
    # Fetch all resources associated with the department username
    resources = Resource.objects.filter(department_name=department_username)
    
    for resource in resources:
        resource.filename = basename(resource.file.name)
    
    # Pass the resources to the template context
    return render(request, 'department_template/manage_resources.html', {'resources': resources})

def update_resource(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    if request.method == 'POST':
        # Update resource fields based on form input
        resource.description = request.POST.get('description')
        
        # Handle file upload
        if 'file' in request.FILES:
            resource.file = request.FILES['file']
        
        # Add more fields as needed
        resource.save()
        messages.success(request, 'Resource updated successfully!')
        return redirect('manage_resources')  # Redirect to the manage_resources page after successful update
    else:
        return redirect('manage_resources')   # Redirect to the manage_resources page if the request method is not POSTect('manage_resources')   # Redirect to the manage_resources page if the request method is not POST

def delete_resource(request, resource_id):
    if request.method == 'POST':
        try:
            resource = Resource.objects.get(pk=resource_id)
            resource.delete()
            messages.success(request, 'Resource deleted successfully.')
        except Resource.DoesNotExist:
            messages.error(request, 'Resource does not exist.')
    return redirect('manage_resources')

def manage_questions(request):
    department_username = request.user.username
    questions = Question.objects.filter(exam__department_name=department_username).select_related('exam').all()
    return render(request, 'department_template/manage_question.html', {'questions': questions})

    

def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('manage_questions')  # Correct URL pattern name here
    
    return redirect('manage_questions')  # Correct URL pattern name here


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

    # Retrieve difficulty choices
    DIFFICULTY_CHOICES = Exam.DIFFICULTY_CHOICES

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

    return render(request, 'department_template/manage_exam.html', {'exams': exams, 'DIFFICULTY_CHOICES': DIFFICULTY_CHOICES})


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
        exam.attempts_allowed = request.POST.get('attempts_allowed')
        exam.difficulty =  request.POST.get('exam_difficulty')
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

def update_course(request, course_id):
    if request.method == 'POST':
        try:
            # Retrieve the course object based on the course_id
            course = Course.objects.get(pk=course_id)
            # Update course fields based on form input
            course.title = request.POST.get('course_title')
            course.description = request.POST.get('course_description')
            course.prerequisites = request.POST.get('course_prerequisites')
            course.learning_outcomes = request.POST.get('course_learning_outcomes')
            course.is_active = request.POST.get('course_is_active') == 'on'  # Convert checkbox value to boolean
            # Handle updating resource file
            if 'course_resource' in request.FILES:
                course.resource = request.FILES['course_resource']
            # Handle updating thumbnail file
            if 'course_thumbnail' in request.FILES:
                course.thumbnail = request.FILES['course_thumbnail']
            # Save the updated course
            course.save()
            messages.success(request, 'Course updated successfully!')
        except Course.DoesNotExist:
            messages.error(request, 'Course not found!')
    return redirect('manage_courses')  # Redirect to the manage_courses page after update


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
    return render(request, 'department_template/manage_tutorials.html', {'tutorials': tutorials, 'courses': courses})

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
            messages.success(request, 'Course Added successfully!')
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
            messages.success(request, 'Tutorial Added successfully!')
            return redirect('add_tutorial')  # Redirect to the same page after adding a tutorial
    else:
        department_name = request.user.username  # Get department name from user
        courses = Course.objects.filter(department_name=department_name)  # Filter courses by department
        # Pass the department to the form
        form = TutorialForm(department=department_name)
        
    return render(request, 'department_template/add_tutorial.html', {
        'form': form,
    })
    
 
def update_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    if request.method == 'POST':
        form = TutorialForm(request.POST, instance=tutorial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tutorial updated successfully!')
            return redirect('manage_tutorials')
    else:
        form = TutorialForm(instance=tutorial)
        department_name = request.user.username
        courses = Course.objects.filter(department_name=department_name)
    return render(request, 'department_template/update_tutorial.html', {'form': form, 'courses': courses})


def delete_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    if request.method == 'POST':
        tutorial.delete()
        messages.success(request, 'Tutorial deleted successfully!')
    return redirect('manage_tutorials')
 

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

    # Retrieve exams along with information about whether each exam has been submitted by the current user
    exams_with_submission = []
    for exam in exams:
        submitted_by_current_user = exam.submitted_by.filter(pk=request.user.pk).exists()
        exams_with_submission.append((exam, submitted_by_current_user))

    return render(request, 'student_template/view_exams.html', {'exams_with_submission': exams_with_submission})



from django.shortcuts import render
from django.db.models import Prefetch
from .models import Exam, Question, Choice

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question  # Import your Exam and Question models

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question  # Import your Exam and Question models

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Exam, Question
from random import shuffle

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
    questions = list(Question.objects.filter(exam=exam).prefetch_related('choice_set'))
    shuffle(questions)  # Shuffle the questions

    context = {
        'exam': exam,
        'questions': questions,
    }

    return render(request, 'student_template/exam_detail.html', context)




# views.py
from django.shortcuts import render, redirect
from .models import Result, Exam, Question, Choice
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, Choice, Result
from django.shortcuts import redirect

from django.shortcuts import render, redirect, get_object_or_404
from .models import Result, Exam, Question, Choice
from .models import ExamSubmission

def submit_exam(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    questions = Question.objects.filter(exam=exam)

    if request.method == 'POST':
        # Calculate the number of correct answers
        correct_answers = 0

        # Initialize dictionary to store user answers
        user_answers = {}

        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}', None)
            if selected_choice_id:
                selected_choice = Choice.objects.get(pk=selected_choice_id)
                if selected_choice.is_correct:
                    correct_answers += 1

                # Store user answer in session
                user_answers[str(question.id)] = selected_choice_id

        # Store user answers in session
        request.session['user_answers'] = user_answers

        # Store the result in the database
        result = Result.objects.create(student=request.user, exam=exam, score=correct_answers)

        # Record the submission
        ExamSubmission.objects.create(exam=exam, user=request.user)

        return render(request, 'student_template/exam_submitted.html', {
            'correct_answers': correct_answers,
            'total_questions': len(questions),
            'result': result,
        })

    return redirect('view_exams')  # Redirect to the view_exams page if it's not a POST request
  # Redirect to the view_exams page if it's not a POST request


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

    # Retrieve user answers from the session
    user_answers = request.session.get('user_answers', {})

    # Serialize the selected choices into a dictionary
    selected_choices = {str(question.id): str(user_answers.get(str(question.id))) for question in questions}

    return render(request, 'student_template/result.html', {
        'result': result,
        'questions_with_choices': questions_with_choices,
        'selected_choices': selected_choices,
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
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_view')
def enter_exam_code(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Retrieve the number of questions for the exam
    num_questions = exam.question_set.count()

    # Get the maximum attempts allowed for the exam
    max_attempts = exam.attempts_allowed

    # Get the session key for the exam code
    session_key = f'exam_code_{exam_id}'

    # Initialize attempt count to 0
    attempt_count = request.session.get(f'attempt_count_{exam_id}', 0)

    # Calculate attempts remaining
    attempts_remaining = max_attempts - attempt_count

    if request.method == 'POST':
        entered_exam_code = request.POST.get('exam_code', '').strip()

        if entered_exam_code:
            if entered_exam_code == exam.exam_code:
                # Check if the attempt count is less than the maximum allowed attempts
                if attempt_count < max_attempts:
                    # Increment the attempt count
                    attempt_count += 1
                    # Store the updated attempt count in the session
                    request.session[f'attempt_count_{exam_id}'] = attempt_count
                    # Store the entered exam code in the session
                    request.session[session_key] = entered_exam_code
                    # Redirect to the exam detail page if the entered code is correct and attempts are within limit
                    return redirect('exam_detail', exam_id=exam_id)
                else:
                    messages.error(request, 'You have reached the maximum number of attempts for this exam.')
            else:
                messages.error(request, 'Invalid exam code. Please try again.')
        else:
            messages.error(request, 'Please enter a valid exam code.')

    return render(request, 'student_template/enter_exam_code.html', {'exam': exam, 'num_questions': num_questions, 'attempts_remaining': attempts_remaining})

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

from os.path import basename
from django.shortcuts import render
from .models import Resource

@login_required(login_url='login_view')
@user_passes_test(lambda user: user.is_student, login_url='NoPage')
def materials(request):
    # Retrieve the logged-in student's department name
    department_name = request.user.department_name

    # Filter resources based on the student's department name
    resources = Resource.objects.filter(department_name=department_name)

    # Extract filenames from file paths
    for resource in resources:
        resource.filename = basename(resource.file.name)

    context = {
        'resources': resources,
    }
    return render(request, 'student_template/materials.html', context)


####################/Student Views/###############################




def logout_view(request):
    logout(request)
    return redirect('login_view')

def NoPage(request):
    return render(request,'404.html')

from django.shortcuts import render, redirect
from .forms import UploadPdfForm
from .utils import extract_questions_with_choices_from_pdf
from .models import Exam, Question, Choice

def upload_pdf_view(request):
    questions_with_choices = None

    # Fetch queryset of exams relevant to the user's department
    department_name = request.user.username  # Assuming you have a user object with department_name
    exam_queryset = Exam.objects.filter(department_name=department_name)

    if request.method == 'POST':
        form = UploadPdfForm(request.POST, request.FILES, department_queryset=exam_queryset)
        if form.is_valid():
            # Get the selected exam
            selected_exam = Exam.objects.get(pk=form.cleaned_data['exam'])
            
            # Extract questions with choices from the uploaded PDF file
            pdf_file = request.FILES['pdf_file']
            questions_with_choices = extract_questions_with_choices_from_pdf(pdf_file)

            # Save the questions and choices in session for preview
            request.session['questions_with_choices'] = questions_with_choices
            request.session['selected_exam'] = selected_exam.id
            
            # Redirect to the preview page
            return redirect('preview_questions')  # Create a URL pattern named 'preview_questions' for the preview page
    else:
        # Initialize the form with the exam queryset
        form = UploadPdfForm(department_queryset=exam_queryset)
    
    return render(request, 'department_template/import_question.html', {'form': form})

def preview_questions_view(request):
    questions_with_choices = request.session.get('questions_with_choices')
    selected_exam_id = request.session.get('selected_exam')
    selected_exam = None
    
    # Check if selected_exam_id exists and get the Exam object
    if selected_exam_id:
        try:
            selected_exam = Exam.objects.get(pk=selected_exam_id)
        except Exam.DoesNotExist:
            # Handle the case where the Exam object does not exist
            # You might want to redirect or render an error page
            pass
    
    # Check if necessary session data is missing
    if not questions_with_choices or not selected_exam:
        # Check if questions_with_choices is empty or None
        if not questions_with_choices:
            message = "Please upload a file with correct format."
        else:
            message = "Please select an exam."
        
        # Add the message to the messages framework
        messages.warning(request, message)
        
        # Redirect to the upload page if session data is missing
        return redirect('upload_pdf_view')  # Replace 'upload_pdf' with the name of your upload page URL pattern
    
    if request.method == 'POST':
        # Get the selected choices from POST data
        selected_choices = {}
        for key, value in request.POST.items():
            if key.startswith('selected_choice_'):
                question_number = key.split('_')[2]  # Extract the question number from the key
                selected_choices[question_number] = value  # Store the selected choice for this question

        # If the user confirms, save questions and choices to the database
        for qwc in questions_with_choices:
            question = Question.objects.create(exam=selected_exam, content=qwc['question'])
            for choice_text in qwc['choices']:
                # Check if this choice is selected
                is_correct = choice_text in selected_choices.values()
                Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)
        
        # Clear session data
        del request.session['questions_with_choices']
        del request.session['selected_exam']
        
        # Add success message
        messages.success(request, 'Questions added successfully!')
        
        # Redirect to a success page or any other desired page
        return redirect('manage_questions')  # Replace 'manage_questions' with the name of your success page URL pattern
    
    return render(request, 'department_template/preview_questions.html', {'questions_with_choices': questions_with_choices})


from .forms import EditQuestionForm, EditChoiceFormSet  # Import the EditQuestionForm and EditChoiceFormSet

def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Pass department username to the form
    form = EditQuestionForm(instance=question, department_username=request.user.username)
    formset = EditChoiceFormSet(instance=question)

    if request.method == 'POST':
        form = EditQuestionForm(request.POST, instance=question, department_username=request.user.username)
        formset = EditChoiceFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Questions Updated successfully!')
            return redirect('manage_questions')

    return render(request, 'department_template/edit_question.html', {'form': form, 'formset': formset, 'question': question})


from django.db.models import Avg, Max, Min, Count, Subquery, OuterRef
from django.shortcuts import render
from .models import Exam, Result

def exam_scores_table(request):
    # Get the department of the current user
    user_department = request.user.username
    
    # Subquery to count the number of questions for each exam
    num_questions_subquery = Subquery(
        Exam.objects.filter(id=OuterRef('exam')).annotate(
            num_questions=Count('question')
        ).values('num_questions')
    )
    
    # Aggregate exam scores for each exam in the department
    aggregate_data = Result.objects.filter(exam__department_name=user_department).values(
        'exam__name'
    ).annotate(
        num_students=Count('student', distinct=True),  # Count the number of distinct students for each exam
        average_score=Avg('score'),
        highest_score=Max('score'), 
        lowest_score=Min('score'),
        num_questions=num_questions_subquery,
    )

    # Process the aggregated data
    total_students = 0
    for data in aggregate_data:
        # Initialize counters for passed and failed students
        passed_students_count = 0
        failed_students_count = 0
        
        # Calculate the pass/fail threshold
        pass_fail_threshold = data['num_questions'] // 2
        
        # Check each student's score against the pass/fail threshold
        for result in Result.objects.filter(exam__name=data['exam__name']):
            if result.score >= pass_fail_threshold:
                passed_students_count += 1
            else:
                failed_students_count += 1
        
        # Add the counts to the data dictionary
        data['passed_students_count'] = passed_students_count
        data['failed_students_count'] = failed_students_count
        
        # Update total students count
        total_students += passed_students_count + failed_students_count

    return render(request, 'department_template/report.html', {'exam_scores_data': aggregate_data, 'total_students': total_students})



def delete_report(request, exam_name):
    # Get the exam object based on the exam name
    exam = get_object_or_404(Exam, name=exam_name)
    
    # Delete all results associated with the exam
    Result.objects.filter(exam=exam).delete()
    
    return redirect('exam_scores_table')  # Redirect back to the exam scores table page





def manage_instructors(request):
    # Retrieve the department name from the logged-in user
    department_name = request.user.username
    
    # Filter instructors based on the department name
    instructors = User.objects.filter(department_name=department_name, is_instructor=True)
    
    return render(request, 'department_template/view_instructor.html', {'instructors': instructors})


# Add Instructor View
@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def add_instructor(request):
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST, department_name=request.user.username)
        if form.is_valid():
            # Generate the password
            password = form.generate_password()

            try:
                user = form.save(commit=False)
                user.is_instructor = True
                user.set_password(password)  # Hash the password
                user.save()
                success_msg = 'Instructor registered successfully!'

                # Send email
                subject = 'Instructor Account Verification'
                html_message = render_to_string('email/instructor_account_email.html', {
                    'user': user,
                    'password': password,  # Pass the generated password to the email template
                    # 'login_url': 'http://127.0.0.1:8000/login/',  # Provide the login URL
                })
                plain_message = strip_tags(html_message)  # Strip HTML tags for plain text message
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = user.email
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            except Exception as e:
                error_msg = f'An error occurred: {str(e)}'
        else:
            error_msg = 'Form is not valid'
    else:
        form = InstructorRegistrationForm(department_name=request.user.username)
    
    return render(request, 'department_template/add_instructor.html', {'form': form})


    

@login_required(login_url='login_view')
@user_passes_test(is_department, login_url='NoPage')
def delete_instructor(request, username):
    if request.method == 'POST':
        try:
            # Retrieve the user (instructor) by username
            instructor = User.objects.get(username=username)
            # Delete the instructor
            instructor.delete()
            messages.success(request, 'Instructor deleted successfully!')
        except User.DoesNotExist:
            messages.error(request, 'Instructor not found!')

    # Redirect to a relevant page after deletion (e.g., manage_instructors)
    return redirect('manage_instructors')



####################### Instructor Views ########################

@login_required(login_url='login_view')
@user_passes_test(is_instructor, login_url='NoPage')
def instructor_home(request):
    return render(request, 'teacher_template/dashboard.html')


@login_required(login_url='login_view')
@user_passes_test(is_instructor, login_url='NoPage')
def view_students(request):
    # Get the department of the logged-in teacher
    teacher_department = request.user.department_name  # Assuming department is a ForeignKey field on the teacher model

    # Filter students based on the department of the teacher
    students = User.objects.filter(is_student=True, department_name=teacher_department)

    return render(request, 'teacher_template/view_student.html', {'students': students})


@login_required(login_url='login_view')
@user_passes_test(is_instructor, login_url='NoPage')
def inst_view_exams(request):
    # Get the department of the logged-in teacher
    teacher_department = request.user.department_name  # Assuming department is a ForeignKey field on the teacher model

    # Filter exams based on the department of the teacher
    exams = Exam.objects.filter(department_name=teacher_department).annotate(num_questions=Count('question'))
   

    return render(request, 'teacher_template/view_exam.html', {'exams': exams})



@login_required(login_url='login_view')
@user_passes_test(is_instructor, login_url='NoPage')
def view_courses_inst(request):
    # Get the department of the logged-in instructor
    instructor_department = request.user.department_name  # Assuming department is a ForeignKey field on the instructor model

    # Filter courses based on the department of the instructor
    courses = Course.objects.filter(department_name=instructor_department)

    return render(request, 'teacher_template/view_course.html', {'courses': courses})




@login_required(login_url='login_view')
def inst_add_question(request):
    success_msg = None
    error_msg = None

    department_username = request.user.department_name

    if request.method == 'POST':
        form = QuestionForm(request.POST, department_username=department_username)
        formset = ChoiceFormSet(request.POST, instance=form.instance)
        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            messages.success(request, 'Questions added successfully!')
        else:
            # error_msg = 'Form is not valid'
            print("Form errors outside if:", form.errors, formset.errors)
    else:
        form = QuestionForm(department_username=department_username)
        # Determine the number of extra forms based on the number of additional choice fields submitted
        num_extra = len(request.POST.getlist('form-0-text')) - 1 if request.POST.get('form-0-text') else 2
        formset = ChoiceFormSet(instance=Question(), extra=num_extra)

    return render(request, 'teacher_template/add_question.html', {
        'form': form,
        'formset': formset,
        'success_msg': success_msg,
        'error_msg': error_msg
    })
    



def inst_manage_questions(request):
    department_username = request.user.department_name
    questions = Question.objects.filter(exam__department_name=department_username).select_related('exam').all()
    return render(request, 'teacher_template/manage_questions.html', {'questions': questions})




# from file


def inst_upload_pdf_view(request):
    questions_with_choices = None

    # Fetch queryset of exams relevant to the user's department
    department_name = request.user.department_name  # Assuming you have a user object with department_name
    exam_queryset = Exam.objects.filter(department_name=department_name)

    if request.method == 'POST':
        form = UploadPdfForm(request.POST, request.FILES, department_queryset=exam_queryset)
        if form.is_valid():
            # Get the selected exam
            selected_exam = Exam.objects.get(pk=form.cleaned_data['exam'])
            
            # Extract questions with choices from the uploaded PDF file
            pdf_file = request.FILES['pdf_file']
            questions_with_choices = extract_questions_with_choices_from_pdf(pdf_file)

            # Save the questions and choices in session for preview
            request.session['questions_with_choices'] = questions_with_choices
            request.session['selected_exam'] = selected_exam.id
            
            # Redirect to the preview page
            return redirect('inst_preview_questions')  # Create a URL pattern named 'preview_questions' for the preview page
    else:
        # Initialize the form with the exam queryset
        form = UploadPdfForm(department_queryset=exam_queryset)
    
    return render(request, 'teacher_template/import_question.html', {'form': form})

def inst_preview_questions_view(request):
    questions_with_choices = request.session.get('questions_with_choices')
    selected_exam_id = request.session.get('selected_exam')
    selected_exam = None
    
    # Check if selected_exam_id exists and get the Exam object
    if selected_exam_id:
        try:
            selected_exam = Exam.objects.get(pk=selected_exam_id)
        except Exam.DoesNotExist:
            # Handle the case where the Exam object does not exist
            # You might want to redirect or render an error page
            pass
    
    # Check if necessary session data is missing
    if not questions_with_choices or not selected_exam:
        # Check if questions_with_choices is empty or None
        if not questions_with_choices:
            message = "Please upload a file with correct format."
        else:
            message = "Please select an exam."
        
        # Add the message to the messages framework
        messages.warning(request, message)
        
        # Redirect to the upload page if session data is missing
        return redirect('inst_upload_pdf_view')  # Replace 'upload_pdf' with the name of your upload page URL pattern
    
    if request.method == 'POST':
        # Get the selected choices from POST data
        selected_choices = {}
        for key, value in request.POST.items():
            if key.startswith('selected_choice_'):
                question_number = key.split('_')[2]  # Extract the question number from the key
                selected_choices[question_number] = value  # Store the selected choice for this question

        # If the user confirms, save questions and choices to the database
        for qwc in questions_with_choices:
            question = Question.objects.create(exam=selected_exam, content=qwc['question'])
            for choice_text in qwc['choices']:
                # Check if this choice is selected
                is_correct = choice_text in selected_choices.values()
                Choice.objects.create(question=question, text=choice_text, is_correct=is_correct)
        
        # Clear session data
        del request.session['questions_with_choices']
        del request.session['selected_exam']
        
        # Add success message
        messages.success(request, 'Questions added successfully!')
        
        # Redirect to a success page or any other desired page
        return redirect('inst_manage_questions')  # Replace 'manage_questions' with the name of your success page URL pattern
    
    return render(request, 'teacher_template/preview_questions.html', {'questions_with_choices': questions_with_choices})



def inst_edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Pass department username to the form
    form = EditQuestionForm(instance=question, department_username=request.user.department_name)
    formset = EditChoiceFormSet(instance=question)

    if request.method == 'POST':
        form = EditQuestionForm(request.POST, instance=question, department_username=request.user.department_name)
        formset = EditChoiceFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Questions Updated successfully!')
            return redirect('inst_manage_questions')

    return render(request, 'teacher_template/edit_question.html', {'form': form, 'formset': formset, 'question': question})


def inst_delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('inst_manage_questions')  # Correct URL pattern name here
    
    return redirect('inst_manage_questions')  # Correct URL pattern name here



def inst_manage_resources(request):
    # Get the department username of the logged-in user
    department_username = request.user.department_name
    added_by_username = request.user.username
    
    # Fetch all resources associated with the department username and added by the logged-in user
    resources = Resource.objects.filter(department_name=department_username, added_by=added_by_username)
    
    for resource in resources:
        resource.filename = basename(resource.file.name)
    
    # Pass the resources to the template context
    return render(request, 'teacher_template/manage_resources.html', {'resources': resources})



def inst_add_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.department_name = request.user.department_name  # Assuming department_name is associated with the user
            resource.added_by = request.user.username  # Set the added_by field to the username of the logged-in user
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('inst_manage_resources')
    else:
        form = ResourceForm()
    return render(request, 'teacher_template/add_resource.html', {'form': form})


def inst_add_tutorial(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tutorial Added successfully!')
            return redirect('inst_add_tutorial')  # Redirect to the same page after adding a tutorial
    else:
        department_name = request.user.department_name  # Get department name from user
        courses = Course.objects.filter(department_name=department_name)  # Filter courses by department
        # Pass the department to the form
        form = TutorialForm(department=department_name)
        
    return render(request, 'teacher_template/add_tutorial.html', {
        'form': form,
    })
 

def inst_manage_tutorials(request):
    department_name = request.user.department_name
    courses = Course.objects.filter(department_name=department_name)
    tutorials = Tutorial.objects.filter(course__in=courses)
    return render(request, 'teacher_template/manage_tutorials.html', {'tutorials': tutorials, 'courses': courses})



def inst_delete_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    if request.method == 'POST':
        tutorial.delete()
        messages.success(request, 'Tutorial deleted successfully!')
    return redirect('inst_manage_tutorials')


def inst_update_tutorial(request, tutorial_id):
    tutorial = get_object_or_404(Tutorial, pk=tutorial_id)
    if request.method == 'POST':
        form = TutorialForm(request.POST, instance=tutorial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tutorial updated successfully!')
            return redirect('inst_manage_tutorials')
    else:
        form = TutorialForm(instance=tutorial)
        department_name = request.user.department_name
        courses = Course.objects.filter(department_name=department_name)
    return render(request, 'teacher_template/update_tutorial.html', {'form': form, 'courses': courses})



def inst_delete_resource(request, resource_id):
    if request.method == 'POST':
        try:
            resource = Resource.objects.get(pk=resource_id)
            resource.delete()
            messages.success(request, 'Resource deleted successfully.')
        except Resource.DoesNotExist:
            messages.error(request, 'Resource does not exist.')
    return redirect('inst_manage_resources')


def inst_update_resource(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id)
    if request.method == 'POST':
        # Update resource fields based on form input
        resource.description = request.POST.get('description')
        
        # Handle file upload
        if 'file' in request.FILES:
            resource.file = request.FILES['file']
        
        # Add more fields as needed
        resource.save()
        messages.success(request, 'Resource updated successfully!')
        return redirect('inst_manage_resources')  # Redirect to the manage_resources page after successful update
    else:
        return redirect('inst_manage_resources')   # Redirect to the manage_resources page if the request method is not POSTect('manage_resources')   # Redirect to the manage_resources page if the request method is not POST

####################### /Instructor Views ########################



#################### notification ###################


from .models import Notification

from django.http import JsonResponse

def count_department_notifications(request):
    # Fetch notifications for the department
    department_notifications = Notification.objects.filter(department=request.user.username)
    
    # Fetch the notification count for the department
    department_notifications_count = department_notifications.count()
    
    # Serialize the notifications
    serialized_notifications = [{'message': notification.message} for notification in department_notifications]

    return JsonResponse({'notifications': serialized_notifications, 'count': department_notifications_count})




def department_notifications(request):
    # Fetch notifications for the department
    department_notifications = Notification.objects.filter(department=request.user.username)
    return render(request, 'department_template/notifications.html', {'notifications': department_notifications})

#################### notification ###################