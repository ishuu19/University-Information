from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='university_profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    image_url = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AcademicBackground(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='university_academic_backgrounds')
    school_name = models.CharField(max_length=255)
    level_completed = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=255)
    result_type = models.CharField(max_length=50)
    result_value = models.CharField(max_length=20)
    completion_year = models.IntegerField()
    start_year = models.IntegerField()
    additional_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_background'
        ordering = ['-completion_year']

    def __str__(self):
        return f"{self.level_completed} at {self.school_name}"

class UserDocument(models.Model):
    DOCUMENT_TYPES = [
        ('diploma', 'Diploma'),
        ('transcript', 'Transcript'),
        ('resume', 'Resume'),
        ('passport', 'Passport'),
        ('standardized_test', 'Standardized Test'),
        ('language_test', 'Language Test'),
        ('recommendation', 'Recommendation'),
        ('eca', 'ECA'),
        ('other', 'Other'),
    ]
    
    DOCUMENT_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file_path = models.TextField()
    original_filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    document_status = models.CharField(max_length=10, choices=DOCUMENT_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'user_documents'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.original_filename}"

class SavedItem(models.Model):
    ITEM_TYPES = [
        ('uni', 'University'),
        ('prog', 'Program'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='university_saved_items')
    item_type = models.CharField(max_length=4, choices=ITEM_TYPES)
    item_id = models.IntegerField()
    saved_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item_type', 'item_id')

    def __str__(self):
        return f"{self.get_item_type_display()} - ID: {self.item_id}" 