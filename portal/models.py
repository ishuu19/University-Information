from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UniversityType(models.Model):
    type_name = models.CharField(max_length=10, choices=[
        ('Private', 'Private'),
        ('Public', 'Public'),
        ('Other', 'Other')
    ])

    class Meta:
        managed = False
        db_table = 'university_type'

    def __str__(self):
        return self.type_name

class University(models.Model):
    name = models.CharField(max_length=255)
    two_line_info = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    world_university_ranking = models.IntegerField(null=True, blank=True)
    type = models.ForeignKey(UniversityType, on_delete=models.SET_NULL, null=True)
    founded_year = models.IntegerField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'university'

    def __str__(self):
        return self.name

class UniversityContact(models.Model):
    university = models.OneToOneField(University, on_delete=models.CASCADE, primary_key=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=50, null=True, blank=True)
    uni_website = models.URLField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'university_contact'

class UniversityDescription(models.Model):
    university = models.OneToOneField(University, on_delete=models.CASCADE, primary_key=True)
    short_description = models.TextField(null=True, blank=True)
    housing_description = models.CharField(max_length=255, null=True, blank=True)
    dining_description = models.CharField(max_length=255, null=True, blank=True)
    student_org_description = models.CharField(max_length=255, null=True, blank=True)
    athletics_description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'university_description'

class UniversityStats(models.Model):
    university = models.OneToOneField(University, on_delete=models.CASCADE, primary_key=True)
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    total_reviews = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(null=True, blank=True)
    total_country_students = models.IntegerField(null=True, blank=True)
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    student_faculty_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    avg_tuition = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_cost_of_living = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'university_stats'

class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'degree'

    def __str__(self):
        return self.name

class Field(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'field'

    def __str__(self):
        return self.name

class Program(models.Model):
    name = models.CharField(max_length=255)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.SET_NULL, null=True)
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True)
    program_overview = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'program'

    def __str__(self):
        return f"{self.name} - {self.university.name}"

class ProgramContact(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, primary_key=True)
    program_email = models.EmailField(null=True, blank=True)
    program_phone = models.CharField(max_length=50, null=True, blank=True)
    program_website = models.URLField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'program_contact'

class ProgramSchedule(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, primary_key=True)
    duration = models.CharField(max_length=50, null=True, blank=True)
    credits = models.IntegerField(null=True, blank=True)
    start_semester = models.CharField(max_length=10, choices=[
        ('Fall', 'Fall'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter')
    ], null=True, blank=True)
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    application_opens_date = models.DateField(null=True, blank=True)
    early_decision = models.DateField(null=True, blank=True)
    regular_decision = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    result_publish = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'program_schedule'

class ProgramRequirements(models.Model):
    program = models.OneToOneField(Program, on_delete=models.CASCADE, primary_key=True)
    tuition = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taught_language = models.CharField(max_length=50, null=True, blank=True)
    test_score_SAT = models.IntegerField(null=True, blank=True)
    test_score_TOEFL = models.IntegerField(null=True, blank=True)
    test_score_IELTS = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    additional_req = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'program_requirements'

class FinancialAidAndScholarships(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    aid_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type_and_for_whom = models.TextField(null=True, blank=True)
    eligibility = models.TextField(null=True, blank=True)
    renewal_criteria = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'financial_aid_and_scholarships'

class ProfessionalScopes(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100)
    more_depth_in_profession = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'professional_scopes'

class ProgramReviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    graduation_year = models.IntegerField(null=True, blank=True)
    review = models.TextField()
    posted_date = models.DateField()
    helpful_votes = models.IntegerField(default=0)
    not_helpful_votes = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'program_reviews'
        ordering = ['-posted_date']

    def __str__(self):
        return f"Review by {self.name} for {self.program.name}"

class ReviewVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(ProgramReviews, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'review_votes'
        unique_together = ('user', 'review')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @classmethod
    def from_db_user(cls, user):
        """Create a profile from a Django user"""
        profile = cls(user=user)
        return profile

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

class Application(models.Model):
    """Model for university applications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    start_term = models.CharField(max_length=50)
    personal_statement = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s application to {self.program.name}"

class SavedUniversity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_universities')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'saved_universities'
        unique_together = ('user', 'university')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.university.name}"

class SavedProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_programs')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'saved_program'
        unique_together = ('user', 'program')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.program.name}"

class UserDocuments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=[
        ('diploma', 'Diploma'),
        ('transcript', 'Academic Transcript'),
        ('resume', 'Resume'),
        ('passport', 'Passport'),
        ('standardized_test', 'Standardized Test Results'),
        ('language_test', 'Language Test Results'),
        ('recommendation', 'Letter of Recommendation'),
        ('eca', 'Educational Credential Assessment'),
        ('other', 'Other Documents')
    ])
    file_path = models.TextField()
    original_filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    document_status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], default='pending')
    notes = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'user_documents'

    def __str__(self):
        return f"{self.user.username} - {self.document_type} - {self.original_filename}"

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50, choices=[
        ('application', 'Application Update'),
        ('system', 'System Notification'),
        ('message', 'New Message'),
    ])
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    @classmethod
    def create_notification(cls, user, title, message, notification_type='system', related_object=None):
        """Helper method to create notifications"""
        notification = cls(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type
        )
        if related_object:
            notification.related_object_id = related_object.id
            notification.related_object_type = related_object.__class__.__name__
        notification.save()
        return notification

class AcademicBackground(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=255)
    level_completed = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    result_type = models.CharField(max_length=50)
    result_value = models.CharField(max_length=20)
    completion_year = models.IntegerField()
    start_year = models.IntegerField()
    additional_info = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'academic_background'
        ordering = ['-completion_year']

    def __str__(self):
        return f"{self.school_name} - {self.level_completed} ({self.completion_year})"

class SavedItems(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=4, choices=[
        ('uni', 'University'),
        ('prog', 'Program')
    ])
    item_id = models.IntegerField()
    saved_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'saved_items'

    def __str__(self):
        return f"{self.user.username} - {self.item_type} - {self.item_id}"

    def get_item(self):
        """Get the actual university or program object"""
        if self.item_type == 'uni':
            return University.objects.get(id=self.item_id)
        elif self.item_type == 'prog':
            return Program.objects.get(id=self.item_id)
