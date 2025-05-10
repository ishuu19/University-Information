from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # University URLs
    path('universities/', views.university_list, name='university_list'),
    path('university/<int:pk>/', views.university_detail, name='university_detail'),
    path('university/<int:pk>/save/', views.save_university, name='save_university'),
    
    # Program URLs
    path('programs/', views.program_list, name='program_list'),
    path('program/<int:pk>/', views.program_detail, name='program_detail'),
    path('program/<int:pk>/save/', views.save_program, name='save_program'),
    path('program/<int:program_id>/review/', views.submit_program_review, name='submit_program_review'),
    path('programs/<int:program_id>/review/<int:review_id>/delete/', views.delete_program_review, name='delete_program_review'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/documents/upload/', views.upload_documents, name='upload_documents'),
    path('profile/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('profile/add-academic-record/', views.add_academic_record, name='add_academic_record'),
    path('profile/delete-academic-record/<int:record_id>/', views.delete_academic_record, name='delete_academic_record'),
    
    # Application URLs
    path('applications/', views.application_list, name='application_list'),
    path('applications/new/<int:program_id>/', views.new_application, name='new_application'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/status/', views.application_status, name='application_status'),
    path('applications/<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('applications/<int:pk>/delete/', views.delete_application, name='delete_application'),
    
    # Notification URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Other URLs
    path('saved-universities/', views.saved_universities, name='saved_universities'),
    path('compare-universities/', views.compare_universities, name='compare_universities'),
    path('program-search/', views.program_search, name='program_search'),
    
    # Academic Background URLs
    path('academic/edit/<int:academic_id>/', views.edit_academic_background, name='edit_academic_background'),
    path('academic/delete/<int:academic_id>/', views.delete_academic_background, name='delete_academic_background'),
    path('academic/get/<int:academic_id>/', views.get_academic_background, name='get_academic_background'),

    # Saved Items URLs
    path('saved-items/', views.saved_items, name='saved_items'),
    path('saved-items/save/', views.save_item, name='save_item'),
    path('saved-items/<int:item_id>/remove/', views.remove_saved_item, name='remove_saved_item'),

    # Unified Search URL
    path('search/', views.unified_search, name='unified_search'),
] 