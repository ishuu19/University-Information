from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    University, UniversityType, UniversityContact, UniversityDescription, UniversityStats,
    Program, ProgramContact, ProgramSchedule, ProgramRequirements,
    FinancialAidAndScholarships, ProfessionalScopes, ProgramReviews,
    UserProfile, Application, SavedUniversity, SavedProgram, UserDocuments,
    Notification, Degree, Field, SavedItems, AcademicBackground
)

# Register models with admin interface
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'get_email', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    
    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'
    
    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'world_university_ranking', 'type')
    list_filter = ('type', 'country')
    search_fields = ('name', 'country', 'location')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'degree', 'field')
    list_filter = ('degree', 'field', 'university')
    search_fields = ('name', 'university__name', 'degree__name', 'field__name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'program', 'university', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user_id', 'program__name', 'university__name')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)

@admin.register(SavedUniversity)
class SavedUniversityAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'university__name')

@admin.register(SavedProgram)
class SavedProgramAdmin(admin.ModelAdmin):
    list_display = ('user', 'program', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'program__name')

# Register remaining models
admin.site.register(UniversityType)
admin.site.register(Degree)
admin.site.register(Field)
admin.site.register(FinancialAidAndScholarships)
admin.site.register(ProfessionalScopes)
admin.site.register(SavedItems)
admin.site.register(AcademicBackground)
