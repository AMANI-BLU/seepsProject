
from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_view,name ="login_view" ),
    path('home/', home,name ="home" ),
    path('feedback/', feedback,name ="feedback" ),
    path('add_department/', add_department,name ="add_department" ),
    path('view_department/', view_department,name ="view_department" ),
    path('delete_department/<str:email>/', delete_department, name='delete_department'),
    path('update/<str:username>/', update_department, name='update_department'),

      
    
    #department urls
    path('department/', department_home,name ="department_home" ),
    path('logout/', logout_view, name='logout'),
    path('add_student/', add_student,name ="add_student" ),
    path('view_student/', view_student,name ="view_student" ),
    path('add_exam/', add_exam, name='add_exam'),
    path('manage_exam/', manage_exam, name='manage_exam'),
    path('add_question/', add_question, name='add_question'),
    path('manage_questions/', manage_questions, name='manage_questions'),
    path('feedback-management/', feedback_management, name='feedback_management'),
    path('delete_student/<str:username>/', delete_student, name='delete_student'),
    path('update_student/<str:username>/', update_student, name='update_student'),
    path('update_exam/<int:exam_id>/', update_exam, name='update_exam'),
    path('delete_exam/<int:exam_id>/', delete_exam, name='delete_exam'),
    # path('update-question/<int:question_id>/', update_question, name='update_question'),
    path('question/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('delete/course/<int:course_id>/', delete_course, name='delete_course'),
    path('update_course/<int:course_id>/', update_course, name='update_course'),
    path('update-tutorial/<int:tutorial_id>/', update_tutorial, name='update_tutorial'),
    path('delete-tutorial/<int:tutorial_id>/', delete_tutorial, name='delete_tutorial'),
    path('import_student/', import_student, name='import_student'),
    path('change-password/', change_password, name='change_password'),
    path('profile/', profile, name='profile'),
    path('delete-feedback/', delete_feedback, name='delete_feedback'),
    path('manage-resources/', manage_resources, name='manage_resources'),
    path('add-resource/', add_resource, name='add_resource'),
    path('delete-resource/<int:resource_id>/', delete_resource, name='delete_resource'),
        path('update_resource/<int:resource_id>/', update_resource, name='update_resource'),
        
            path('import_question/', upload_pdf_view, name='upload_pdf_view'),
                path('preview/', preview_questions_view, name='preview_questions'),

  






    
    path('manage/courses/', manage_courses, name='manage_courses'),
    path('manage/courses/add/', add_course, name='add_course'),
    path('manage/tutorials/add/', add_tutorial, name='add_tutorial'),
    path('manage/tutorials/', manage_tutorials, name='manage_tutorials'),
    # path('manage/courses/edit/<int:course_id>/', edit_course, name='edit_course'),
    # path('manage/courses/delete/<int:course_id>/', delete_course, name='delete_course'),
    
    

    #student urls
    path('student/', student_home, name='student_home'),
    path('view_exams/', view_exams, name='view_exams'),
    path('exam/<int:exam_id>/', exam_detail, name='exam_detail'),
    path('result/<int:result_id>/', result, name='result'),
    path('submit_exam/<int:exam_id>/', submit_exam, name='submit_exam'),
    path('enter_exam_code/<int:exam_id>/', enter_exam_code, name='enter_exam_code'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('tutorial/<int:course_id>/', tutorial_page, name='tutorial_page'),
    path('materials/', materials, name='materials'),

    #NoPage
    path('nopage/', NoPage, name='NoPage'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
