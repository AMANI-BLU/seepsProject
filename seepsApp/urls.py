
from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', login_view,name ="login_view" ),
    path('home/', home,name ="home" ),
    path('feedback/', feedback,name ="feedback" ),
    path('add_department/', add_department,name ="add_department" ),
    path('view_department/', view_department,name ="view_department" ),
    path('delete_department/<str:email>/', delete_department, name='delete_department'),
    path('update/<str:username>/', update_department, name='update_department'),
    path('delete_departments/', delete_departments, name='delete_departments'),
    path('generate-credential/', generate_credential, name='generate_credential'),

      
    
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

    path('change-password/', change_password, name='change_password'),
    path('profile/', profile, name='profile'),
    path('delete-feedback/', delete_feedback, name='delete_feedback'),
    path('manage-resources/', manage_resources, name='manage_resources'),
    path('add-resource/', add_resource, name='add_resource'),
    path('delete-resource/<int:resource_id>/', delete_resource, name='delete_resource'),
    path('update_resource/<int:resource_id>/', update_resource, name='update_resource'),
        
    path('import_question/', upload_pdf_view, name='upload_pdf_view'),
    path('preview/', preview_questions_view, name='preview_questions'),
    path('edit_question/<int:question_id>/', edit_question, name='edit_question'),
    path('exam-scores/', exam_scores_table, name='exam_scores_table'),
    path('delete-report/<str:exam_name>/', delete_report, name='delete_report'),
                            
                            
    path('manage_instructors/', manage_instructors, name='manage_instructors'),
    path('add_instructor/', add_instructor, name='add_instructor'),
    path('delete_instructor/<str:username>/', delete_instructor, name='delete_instructor'),
    path('update_instructor/<str:username>/', update_instructor, name='update_instructor'),
    path('delete-students/', delete_students, name='delete_students'),
    path('generate-credentials-students/', generate_credentials_students, name='generate_credentials_students'),
    
    path('delete-instructors/', delete_instructors, name='delete_instructors'),
    path('generate-credentials-instructors/', generate_credentials_instructors, name='generate_credentials_instructors'),

 

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),



  






    
    path('manage/courses/', manage_courses, name='manage_courses'),
    path('manage/courses/add/', add_course, name='add_course'),
    path('manage/tutorials/add/', add_tutorial, name='add_tutorial'),
    path('manage/tutorials/', manage_tutorials, name='manage_tutorials'),
    # path('manage/courses/edit/<int:course_id>/', edit_course, name='edit_course'),
    # path('manage/courses/delete/<int:course_id>/', delete_course, name='delete_course'),
    path('delete_selected_students/', delete_selected_students, name='delete_selected_students'),

    

    #student urls
    path('student/', student_home, name='student_home'),
    path('my_profile/', student_profile, name='student_profile'),
    path('view_exams/', view_exams, name='view_exams'),
    path('exam/<int:exam_id>/<int:attempts_remaining>/', exam_detail, name='exam_detail'),
    path('result/<int:result_id>/', result, name='result'),
    path('submit_exam/<int:exam_id>/', submit_exam, name='submit_exam'),
    path('enter_exam_code/<int:exam_id>/', enter_exam_code, name='enter_exam_code'),
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('tutorial/<int:course_id>/', tutorial_page, name='tutorial_page'),
    path('materials/', materials, name='materials'),
    
    path('calendar/', event_calendar, name='event_calendar'),
    path('create/', create_event, name='create_event'),
    path('edit-event/<int:event_id>/', edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),
    path('chatbot/', chatbot, name='chatbot'),

  
   #teacher urls
   path('teacher_home/', instructor_home, name='instructor_home'),
   path('view_students/', view_students, name='view_students'),
   path('inst_exams/', inst_view_exams, name='inst_view_exams'),
   path('view_courses_inst/', view_courses_inst, name='view_courses_inst'),
   path('inst_add_question/', inst_add_question, name='inst_add_question'),
   path('inst_manage_questions/', inst_manage_questions, name='inst_manage_questions'),
   path('inst_import_question/', inst_upload_pdf_view, name='inst_upload_pdf_view'),
   path('inst_preview/', inst_preview_questions_view, name='inst_preview_questions'),
   path('inst_edit_question/<int:question_id>/', inst_edit_question, name='inst_edit_question'),
   path('inst_delete_question/<int:question_id>/delete/', inst_delete_question, name='inst_delete_question'),
   path('inst-manage-resources/', inst_manage_resources, name='inst_manage_resources'),
   path('inst-add-resource/', inst_add_resource, name='inst_add_resource'),
   path('inst_manage/tutorials/add/', inst_add_tutorial, name='inst_add_tutorial'),
   path('inst_manage/tutorials/', inst_manage_tutorials, name='inst_manage_tutorials'),
   path('inst_delete-tutorial/<int:tutorial_id>/', inst_delete_tutorial, name='inst_delete_tutorial'),
   path('inst_update-tutorial/<int:tutorial_id>/', inst_update_tutorial, name='inst_update_tutorial'),
   path('inst_delete-resource/<int:resource_id>/', inst_delete_resource, name='inst_delete_resource'),
   path('inst_update_resource/<int:resource_id>/', inst_update_resource, name='inst_update_resource'),
        

   #notifications
   path('department/notifications/', department_notifications, name='department_notifications'),
   path('count_department/notifications/', count_department_notifications, name='count_department_notifications'),
   path('latest_department_notifications/', latest_department_notifications, name='latest_department_notifications'),
   path('update_notification_status/<int:notification_id>/', update_notification_status, name='update_notification_status'),

   

   #Books Search
    path('book/search/', book_search, name='book_search'),
    path('youtube/', youtube, name='youtube'),
    path('wiki/', wiki, name='wiki'),
    path('dictionary-search/', dictionary_search, name='dictionary_search'),
    path('navigation-options/', navigation_options_view, name='navigation_options'),
    path('study-dashboard/', study_dashboard, name='study_dashboard'),
    path('chat/', chat_room, name='chat_room'),
    path('send-message/', send_message, name='send_message'),
  



   
    #NoPage
    path('nopage/', NoPage, name='NoPage'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
