from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import (
    University, Program, UniversityStats, UniversityDescription, 
    ProgramRequirements, UserProfile, Application, UserDocuments, Notification, SavedUniversity,
    UniversityType, Degree, Field, SavedItems, AcademicBackground
)
from django.core.files.storage import FileSystemStorage
import time
import os
from django.conf import settings
from django.db import connection
from django.utils import timezone
import json

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    """Return one row from a cursor as a dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def home(request):
    try:
        with connection.cursor() as cursor:
            # Get top universities by ranking with their details
            cursor.execute("""
                SELECT 
                    u.id,
                    u.name,
                    u.location,
                    u.country,
                    u.world_university_ranking,
                    u.image_url,
                    u.two_line_info,
                    ut.type_name
                FROM university u
                LEFT JOIN university_type ut ON u.type_id = ut.id
                WHERE u.world_university_ranking IS NOT NULL
                ORDER BY u.world_university_ranking
                LIMIT 6
            """)
            top_universities = dictfetchall(cursor)
            
            # Get unique countries for filter
            cursor.execute("""
                SELECT DISTINCT country 
                FROM university 
                WHERE country IS NOT NULL 
                ORDER BY country
            """)
            countries = [row[0] for row in cursor.fetchall()]
            
            # Get unique university types for filter
            cursor.execute("""
                SELECT DISTINCT type_name 
                FROM university_type 
                WHERE type_name IS NOT NULL 
                ORDER BY type_name
            """)
            university_types = [row[0] for row in cursor.fetchall()]

            # Complex Statistics for Impact Section
            cursor.execute("""
                WITH GlobalStats AS (
                    -- Calculate global statistics
                    SELECT 
                        COUNT(DISTINCT u.id) as total_universities,
                        COUNT(DISTINCT u.country) as total_countries,
                        COALESCE(SUM(u.total_students), 0) as total_students
                    FROM university u
                ),
                ProgramStats AS (
                    -- Calculate program statistics
                    SELECT 
                        COUNT(DISTINCT p.id) as total_programs,
                        COUNT(DISTINCT p.field_id) as total_fields,
                        COUNT(DISTINCT p.degree_id) as total_degrees
                    FROM program p
                ),
                ApplicationStats AS (
                    -- Calculate application success rates and trends
                    SELECT 
                        COUNT(*) as total_applications,
                        COUNT(DISTINCT user_id) as total_applicants
                    FROM applications
                ),
                UniversityAcceptanceStats AS (
                    -- Calculate average acceptance rate per university
                    SELECT AVG(acceptance_rate) as avg_acceptance_rate
                    FROM university
                ),
                ReviewStats AS (
                    -- Calculate review statistics
                    SELECT 
                        COALESCE(AVG(rating), 0) as avg_program_rating,
                        COUNT(*) as total_reviews
                    FROM program_reviews
                ),
                ScholarshipStats AS (
                    -- Calculate scholarship statistics
                    SELECT 
                        COUNT(DISTINCT id) as total_scholarships,
                        COALESCE(MAX(amount), 0) as max_scholarship_amount
                    FROM financial_aid_and_scholarships
                ),
                LanguageStats AS (
                    -- Calculate program language diversity
                    SELECT COUNT(DISTINCT taught_language) as total_languages
                    FROM program
                    WHERE taught_language IS NOT NULL
                )
                SELECT 
                    gs.*,
                    ps.*,
                    app_stats.*,
                    uas.avg_acceptance_rate,
                    rs.*,
                    ss.*,
                    ls.total_languages
                FROM GlobalStats gs
                CROSS JOIN ProgramStats ps
                CROSS JOIN ApplicationStats app_stats
                CROSS JOIN UniversityAcceptanceStats uas
                CROSS JOIN ReviewStats rs
                CROSS JOIN ScholarshipStats ss
                CROSS JOIN LanguageStats ls
            """)
            impact_stats_raw = dictfetchone(cursor)
            
            # Format numbers with commas
            def format_number(n):
                if n is None:
                    return "0"
                if isinstance(n, float):
                    if n.is_integer():
                        n = int(n)
                    else:
                        return f"{n:,.1f}"
                return f"{n:,}"

            # Format the acceptance rate
            acceptance_rate = round(float(impact_stats_raw['avg_acceptance_rate']), 1)
            acceptance_rate_display = f"{acceptance_rate}%"

            impact_stats = {
                'total_universities': format_number(impact_stats_raw['total_universities']),
                'total_countries': format_number(impact_stats_raw['total_countries']),
                'total_students': format_number(impact_stats_raw['total_students']),
                'total_programs': format_number(impact_stats_raw['total_programs']),
                'total_fields': format_number(impact_stats_raw['total_fields']),
                'total_degrees': format_number(impact_stats_raw['total_degrees']),
                'total_applicants': format_number(impact_stats_raw['total_applicants']),
                'total_scholarships': format_number(impact_stats_raw['total_scholarships']),
                'max_scholarship_amount': format_number(impact_stats_raw['max_scholarship_amount']),
                'total_reviews': format_number(impact_stats_raw['total_reviews']),
                'avg_program_rating': round(float(impact_stats_raw['avg_program_rating']), 1),
                'avg_acceptance_rate': acceptance_rate_display,
                'total_languages': format_number(impact_stats_raw['total_languages'])
            }
            
            context = {
                'universities': top_universities,
                'countries': countries,
                'university_types': university_types,
                'impact_stats': impact_stats
            }
            return render(request, 'home.html', context)
    except Exception as e:
        print(f"Error in home view: {str(e)}")
        messages.error(request, 'Error loading home page data.')
        return render(request, 'home.html', {'universities': []})

def university_list(request):
    try:
        with connection.cursor() as cursor:
            # Base query
            query = """
                SELECT DISTINCT
                    u.id,
                    u.name,
                    u.location,
                    u.country,
                    u.world_university_ranking,
                    u.image_url,
                    u.two_line_info,
                    ut.type_name,
                    ut.id as type_id
                FROM university u
                LEFT JOIN university_type ut ON u.type_id = ut.id
                WHERE 1=1
            """
            params = []
    
            # Filter by country
            country = request.GET.get('country')
            if country:
                query += " AND u.country = %s"
                params.append(country)
    
            # Filter by type
            uni_type = request.GET.get('type')
            if uni_type:
                query += " AND ut.type_name = %s"
                params.append(uni_type)
    
            # Filter by ranking range
            min_ranking = request.GET.get('min_ranking')
            if min_ranking and min_ranking.isdigit():
                query += " AND u.world_university_ranking >= %s"
                params.append(int(min_ranking))

            max_ranking = request.GET.get('max_ranking')
            if max_ranking and max_ranking.isdigit():
                query += " AND u.world_university_ranking <= %s"
                params.append(int(max_ranking))
    
            # Search functionality
            search_query = request.GET.get('search')
            if search_query:
                query += """ AND (
                    u.name LIKE %s OR 
                    u.location LIKE %s OR 
                    u.country LIKE %s
                )"""
                search_param = f"%{search_query}%"
                params.extend([search_param, search_param, search_param])
    
            # Sort functionality
            sort_by = request.GET.get('sort', 'ranking')  # Default to ranking if not specified
            if sort_by == 'ranking':
                # Sort by ranking, putting NULL values at the end
                query += """ ORDER BY 
                    CASE 
                        WHEN u.world_university_ranking IS NULL THEN 999999 
                        ELSE u.world_university_ranking 
                    END ASC"""
            elif sort_by == 'name':
                # Sort alphabetically by name
                query += " ORDER BY u.name ASC"
            elif sort_by == 'country':
                # Sort by country, then by name within each country
                query += " ORDER BY u.country ASC, u.name ASC"
            else:
                # Default to ranking sort
                query += """ ORDER BY 
                    CASE 
                        WHEN u.world_university_ranking IS NULL THEN 999999 
                        ELSE u.world_university_ranking 
                    END ASC"""

            # Execute the main query
            cursor.execute(query, params)
            universities = dictfetchall(cursor)
    
            # Get unique values for filters
            cursor.execute("""
                SELECT DISTINCT country 
                FROM university 
                WHERE country IS NOT NULL 
                ORDER BY country
            """)
            countries = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT DISTINCT type_name 
                FROM university_type 
                WHERE type_name IS NOT NULL 
                ORDER BY type_name
            """)
            types = [row[0] for row in cursor.fetchall()]
    
            # Pagination
            paginator = Paginator(universities, 30)  # Show 30 universities per page
            
            # Get the first page parameter if multiple exist
            page_number = request.GET.getlist('page')[0] if request.GET.getlist('page') else 1
            
            try:
                page_number = int(page_number)
                if page_number < 1:
                    page_number = 1
                elif page_number > paginator.num_pages:
                    page_number = paginator.num_pages
            except (ValueError, TypeError, IndexError):
                page_number = 1
                
            page_obj = paginator.page(page_number)
    
            context = {
                'page_obj': page_obj,
                'countries': countries,
                'types': types,
                'selected_country': country,
                'selected_type': uni_type,
                'min_ranking': min_ranking,
                'max_ranking': max_ranking,
                'search_query': search_query,
                'sort_by': sort_by,
            }
            return render(request, 'university_list.html', context)
    except Exception as e:
        print(f"Error in university_list: {str(e)}")
        messages.error(request, 'Error loading universities list.')
        return render(request, 'university_list.html', {'page_obj': None})

def program_list(request):
    try:
        with connection.cursor() as cursor:
            # Base query
            query = """
                SELECT DISTINCT
                    p.id,
                    p.name,
                    p.program_overview,
                    p.duration,
                    p.tuition,
                    p.start_semester,
                    u.name as university_name,
                    u.country as country,
                    d.name as degree_name,
                    f.name as field_name,
                    p.image_url
                FROM program p
                LEFT JOIN university u ON p.university_id = u.id
                LEFT JOIN degree d ON p.degree_id = d.id
                LEFT JOIN field f ON p.field_id = f.id
                WHERE 1=1
            """
            params = []
            
            # Filter by field
            field = request.GET.get('field')
            if field:
                query += " AND f.name = %s"
                params.append(field)
            
            # Filter by degree
            degree = request.GET.get('degree')
            if degree:
                query += " AND d.name = %s"
                params.append(degree)
            
            # Filter by country
            country = request.GET.get('country')
            if country:
                query += " AND u.country = %s"
                params.append(country)
            
            # Filter by tuition range
            min_tuition = request.GET.get('min_tuition')
            if min_tuition:
                query += " AND p.tuition >= %s"
                params.append(min_tuition)
            
            max_tuition = request.GET.get('max_tuition')
            if max_tuition:
                query += " AND p.tuition <= %s"
                params.append(max_tuition)
            
            # Search functionality
            search_query = request.GET.get('search')
            if search_query:
                query += """ AND (
                    p.name LIKE %s OR 
                    p.program_overview LIKE %s OR
                    u.name LIKE %s OR
                    f.name LIKE %s OR
                    d.name LIKE %s
                )"""
                search_param = f"%{search_query}%"
                params.extend([search_param, search_param, search_param, search_param, search_param])
            
            # Sort functionality
            sort_by = request.GET.get('sort')
            if sort_by == 'name':
                query += " ORDER BY p.name"
            elif sort_by == 'country':
                query += " ORDER BY u.country, p.name"
            elif sort_by == 'tuition':
                query += " ORDER BY p.tuition"
            else:
                query += " ORDER BY p.name"  # Default sorting

            # Execute the main query
            cursor.execute(query, params)
            programs = dictfetchall(cursor)
            
            # Get unique values for filters
            cursor.execute("""
                SELECT DISTINCT f.name 
                FROM field f 
                WHERE f.name IS NOT NULL 
                ORDER BY f.name
            """)
            fields = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT DISTINCT d.name 
                FROM degree d 
                WHERE d.name IS NOT NULL 
                ORDER BY d.name
            """)
            degrees = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT DISTINCT u.country 
                FROM university u 
                WHERE u.country IS NOT NULL 
                ORDER BY u.country
            """)
            countries = [row[0] for row in cursor.fetchall()]
            
            # Pagination
            paginator = Paginator(programs, 30)  # Show 30 programs per page
            
            # Get the first page parameter if multiple exist
            page_number = request.GET.getlist('page')[0] if request.GET.getlist('page') else 1
            
            try:
                page_obj = paginator.page(page_number)
            except (PageNotAnInteger, EmptyPage):
                page_obj = paginator.page(1)
            
            context = {
                'page_obj': page_obj,
                'fields': fields,
                'degrees': degrees,
                'countries': countries,
                'selected_field': field,
                'selected_degree': degree,
                'selected_country': country,
                'min_tuition': min_tuition,
                'max_tuition': max_tuition,
                'search_query': search_query,
                'sort_by': sort_by,
            }
            
            return render(request, 'program_list.html', context)
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def university_detail(request, pk):
    """View for displaying university details."""
    try:
        with connection.cursor() as cursor:
            # Get university details
            cursor.execute("""
                SELECT 
                    u.id,
                    u.name,
                    u.location,
                    u.country,
                    u.short_description,
                    u.two_line_info,
                    u.housing_description,
                    u.dining_description,
                    u.student_org_description,
                    u.athletics_description,
                    u.total_students,
                    u.total_country_students,
                    (SELECT AVG(tuition) FROM program WHERE university_id = u.id) as avg_tuition,
                    u.estimated_cost_of_living,
                    u.student_faculty_ratio,
                    u.acceptance_rate,
                    u.world_university_ranking,
                    u.founded_year,
                    u.image_url,
                    u.application_deadline,
                    ut.type_name,
                    uar.id as admission_req_id,
                    uar.req,
                    uar.language_req,
                    uar.standardized_test_scores,
                    uar.extra_docs,
                    uar.university_id,
                    uc.uni_website,
                    uc.contact_phone,
                    uc.contact_email
                FROM university u
                LEFT JOIN university_type ut ON u.type_id = ut.id
                LEFT JOIN uni_admission_requirements uar ON u.id = uar.university_id
                LEFT JOIN university_contact uc ON u.id = uc.university_id
                WHERE u.id = %s
            """, [pk])
            university = dictfetchone(cursor)

            if not university:
                messages.error(request, 'University not found.')
                return redirect('university_list')

            # Get programs
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.program_overview,
                    d.name as degree_name,
                    f.name as field_name
                FROM program p
                LEFT JOIN degree d ON p.degree_id = d.id
                LEFT JOIN field f ON p.field_id = f.id
                WHERE p.university_id = %s
                ORDER BY p.name
            """, [pk])
            programs = dictfetchall(cursor)

            # Get program reviews statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_reviews,
                    COALESCE(AVG(rating), 0) as avg_rating
                FROM program_reviews pr
                JOIN program p ON pr.program_id = p.id
                WHERE p.university_id = %s
            """, [pk])
            review_stats = dictfetchone(cursor)
            
            # Update university with review statistics
            university['total_reviews'] = review_stats['total_reviews']
            university['avg_rating'] = round(review_stats['avg_rating'], 1)

            # Check if university is saved
            is_saved = False
            if request.user.is_authenticated:
                cursor.execute("""
                    SELECT 1 FROM saved_items si
                    WHERE si.user_id = %s 
                    AND si.item_type = 'UNIV' 
                    AND si.item_id = %s
                """, [request.user.id, pk])
                is_saved = bool(cursor.fetchone())

            # Get university statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT a.id) as total_applications,
                    COUNT(DISTINCT CASE WHEN a.status = 'accepted' THEN a.id END) as accepted_applications,
                    COUNT(DISTINCT CASE WHEN a.status = 'rejected' THEN a.id END) as rejected_applications,
                    COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN a.id END) as pending_applications
                FROM applications a
                WHERE a.university_id = %s
            """, [pk])
            stats = dictfetchone(cursor)
    
            context = {
                'university': university,
                'programs': programs,
                'is_saved': is_saved,
                'stats': stats,
            }
            return render(request, 'universities/university_detail.html', context)
    except Exception as e:
        print(f"Error in university_detail: {str(e)}")
        messages.error(request, f'Error loading university details: {str(e)}')
        return redirect('university_list')

@login_required
def program_detail(request, pk):
    """View for displaying program details."""
    try:
        with connection.cursor() as cursor:
            # Get program details with university, degree, and field information
            cursor.execute("""
                SELECT 
                    p.*,
                    u.name as university_name,
                    u.location as university_location,
                    u.country as university_country,
                    d.name as degree_name,
                    f.name as field_name
                FROM program p
                LEFT JOIN university u ON p.university_id = u.id
                LEFT JOIN degree d ON p.degree_id = d.id
                LEFT JOIN field f ON p.field_id = f.id
                WHERE p.id = %s
            """, [pk])
            program = dictfetchone(cursor)

            if not program:
                messages.error(request, 'Program not found.')
                return redirect('program_list')

            # Check if program is saved
            is_saved = False
            if request.user.is_authenticated:
                cursor.execute("""
                    SELECT 1 FROM saved_items si
                    WHERE si.user_id = %s 
                    AND si.item_type = 'PROG' 
                    AND si.item_id = %s
                """, [request.user.id, pk])
                is_saved = bool(cursor.fetchone())

            # Get key modules
            cursor.execute("""
                SELECT module_name
                FROM program_key_module
                WHERE program_id = %s
            """, [pk])
            modules_raw = dictfetchall(cursor)
            
            # Process modules (comma-separated values)
            modules = []
            for module in modules_raw:
                module_names = [name.strip() for name in module['module_name'].split(',')]
                for name in module_names:
                    modules.append({
                        'module_name': name,
                        'description': ''  # Empty description since column doesn't exist
                    })
    
            # Get professional scopes
            cursor.execute("""
                SELECT profession, more_depth_in_profession
                FROM professional_scopes
                WHERE program_id = %s
            """, [pk])
            scopes_raw = dictfetchall(cursor)

            # Process scopes (multiple in-depth items per profession)
            scopes = []
            for scope in scopes_raw:
                profession = scope['profession'].strip()
                in_depth_fields = [detail.strip() for detail in scope['more_depth_in_profession'].split(',')]
                scopes.append({
                    'profession': profession,
                    'more_depth_in_profession': in_depth_fields  # a list of strings
                });

    
    # Get program reviews
            cursor.execute("""
                SELECT 
                    pr.*,
                    u.name as university_name
                FROM program_reviews pr
                LEFT JOIN university u ON pr.university_id = u.id
                WHERE pr.program_id = %s
                ORDER BY pr.posted_date DESC
            """, [pk])
            reviews = dictfetchall(cursor)
    
    # Calculate average rating
            avg_rating = sum(review['rating'] for review in reviews) / len(reviews) if reviews else 0

            # Get financial aid and scholarships (top 5)
            cursor.execute("""
                SELECT *
                FROM financial_aid_and_scholarships
                WHERE program_id = %s
                ORDER BY amount DESC
                LIMIT 5
            """, [pk])
            scholarships = dictfetchall(cursor)

            context = {
                'program': program,
                'modules': modules,
                'scopes': scopes,
                'reviews': reviews,
                'avg_rating': avg_rating,
                'scholarships': scholarships,
                'is_saved': is_saved,
            }
            return render(request, 'programs/program_detail.html', context)
    except Exception as e:
        print(f"Error in program_detail: {str(e)}")
        messages.error(request, f'Error loading program details: {str(e)}')
        return redirect('program_list')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomAuthenticationForm()
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Check if username is actually an email
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    messages.error(request, 'No account found with this email address.')
                    return render(request, 'registration/login.html', {'form': form})
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Set session expiry
                    if not remember_me:
                        request.session.set_expiry(0)
                    
                    # Redirect to next page if specified
                    next_url = request.GET.get('next')
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('home')
                else:
                    messages.error(request, 'Your account is not active. Please contact support.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Create UserProfile
                UserProfile.objects.create(user=user)
                
                # Log the user in
                login(request, user)
                
                messages.success(request, 'Registration successful! Welcome to our platform.')
                return redirect('home')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    try:
        with connection.cursor() as cursor:
            # Get user profile data with proper JOIN to auth_user
            cursor.execute("""
                SELECT 
                    au.first_name,
                    au.last_name,
                    au.email,
                    up.phone,
                    up.address,
                    up.bio,
                    up.image_url
                FROM auth_user au
                LEFT JOIN user_profiles up ON au.id = up.user_id
                WHERE au.id = %s
            """, [request.user.id])
            profile = cursor.fetchone()
            
            # Get saved universities with university details
            cursor.execute("""
                SELECT 
                    si.id as saved_item_id,
                    u.id as university_id,
                    u.name as university_name,
                    u.location,
                    u.country,
                    u.world_university_ranking,
                    u.image_url,
                    u.avg_tuition,
                    u.estimated_cost_of_living,
                    u.total_country_students,
                    si.saved_date,
                    si.notes
                FROM saved_items si
                JOIN university u ON si.item_id = u.id
                WHERE si.user_id = %s 
                AND si.item_type = 'UNIV'
                ORDER BY si.saved_date DESC
            """, [request.user.id])
            saved_universities = dictfetchall(cursor)

            # Get saved programs with program details
            cursor.execute("""
                SELECT 
                    si.id as saved_item_id,
                    p.id as program_id,
                    p.name as program_name,
                    p.duration,
                    p.tuition,
                    p.start_semester,
                    p.image_url,
                    u.name as university_name,
                    d.name as degree_name,
                    f.name as field_name,
                    si.saved_date
                FROM saved_items si
                JOIN program p ON si.item_id = p.id
                LEFT JOIN university u ON p.university_id = u.id
                LEFT JOIN degree d ON p.degree_id = d.id
                LEFT JOIN field f ON p.field_id = f.id
                WHERE si.user_id = %s 
                AND si.item_type = 'PROG'
                ORDER BY si.saved_date DESC
            """, [request.user.id])
            saved_programs = dictfetchall(cursor)

            # Get academic background
            cursor.execute("""
                SELECT 
                    id,
                    school_name,
                    level_completed,
                    field_of_study,
                    result_type,
                    result_value,
                    completion_year,
                    start_year,
                    additional_info
                FROM academic_background
                WHERE user_id = %s
                ORDER BY completion_year DESC
            """, [request.user.id])
            academic_history = cursor.fetchall()

            # Get user documents
            cursor.execute("""
                SELECT 
                    id,
                    document_type,
                    file_path,
                    original_filename,
                    upload_date,
                    document_status,
                    notes
                FROM user_documents
                WHERE user_id = %s
                ORDER BY upload_date DESC
            """, [request.user.id])
            documents = cursor.fetchall()

            # Get applications
            cursor.execute("""
                SELECT 
                    a.id,
                    a.start_term,
                    a.personal_statement,
                    a.status,
                    a.created_at,
                    u.name as university_name,
                    p.name as program_name
                FROM applications a
                LEFT JOIN university u ON a.university_id = u.id
                LEFT JOIN program p ON a.program_id = p.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            """, [request.user.id])
            applications = cursor.fetchall()

            # Convert profile tuple to dictionary
            profile_data = {
                'first_name': profile[0] if profile[0] else '',
                'last_name': profile[1] if profile[1] else '',
                'email': profile[2] if profile[2] else '',
                'phone': profile[3] if profile[3] else '',
                'address': profile[4] if profile[4] else '',
                'bio': profile[5] if profile[5] else '',
                'image_url': profile[6] if profile[6] else ''
            }

            # Convert academic history to list of dictionaries
            academic_data = []
            for record in academic_history:
                academic_data.append({
                    'id': record[0],
                    'school_name': record[1],
                    'level_completed': record[2],
                    'field_of_study': record[3],
                    'result_type': record[4],
                    'result_value': record[5],
                    'completion_year': record[6],
                    'start_year': record[7],
                    'additional_info': record[8]
                })

            # Convert documents to list of dictionaries
            document_data = []
            for doc in documents:
                document_data.append({
                    'id': doc[0],
                    'document_type': doc[1],
                    'file_path': doc[2],
                    'original_filename': doc[3],
                    'upload_date': doc[4],
                    'document_status': doc[5],
                    'notes': doc[6]
                })

            # Convert applications to list of dictionaries
            application_data = []
            for app in applications:
                application_data.append({
                    'id': app[0],
                    'start_term': app[1],
                    'personal_statement': app[2],
                    'status': app[3],
                    'created_at': app[4],
                    'university_name': app[5],
                    'program_name': app[6]
                })
    
            context = {
                'profile': profile_data,
                'academic_history': academic_data,
                'documents': document_data,
                'saved_universities': saved_universities,
                'saved_programs': saved_programs,
                'applications': application_data
            }
            return render(request, 'registration/profile.html', context)
    except Exception as e:
        print(f"Error in profile_view: {str(e)}")
        messages.error(request, 'Error loading profile data.')
        return redirect('home')

@login_required
def edit_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        try:
            if 'photo' in request.FILES:
                file = request.FILES['photo']
                allowed_types = ['image/jpeg', 'image/png', 'image/gif']
                if file.content_type not in allowed_types:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid file type. Please upload JPG, PNG, or GIF.'
                    })
                
                if file.size > 5 * 1024 * 1024:
                    return JsonResponse({
                        'success': False,
                        'message': 'File size too large. Maximum size is 5MB.'
                    })
                
                photos_dir = os.path.join(settings.MEDIA_ROOT, 'profile_photos')
                os.makedirs(photos_dir, exist_ok=True)
                
                timestamp = int(time.time())
                original_filename = file.name
                file_extension = original_filename.split('.')[-1].lower()
                safe_filename = f"user_{request.user.id}_{timestamp}.{file_extension}"
                file_path = os.path.join(photos_dir, safe_filename)
                
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                relative_path = os.path.join('profile_photos', safe_filename)
                profile.image_url = relative_path
                profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Profile photo updated successfully',
                    'image_url': os.path.join(settings.MEDIA_URL, relative_path)
                })

            profile.first_name = request.POST.get('first_name')
            profile.last_name = request.POST.get('last_name')
            profile.email = request.POST.get('email')
            profile.phone = request.POST.get('phone')
            profile.address = request.POST.get('address')
            profile.bio = request.POST.get('bio')
            profile.save()
            
            request.user.first_name = profile.first_name
            request.user.last_name = profile.last_name
            request.user.email = profile.email
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
        
    return render(request, 'registration/profile.html', {'profile': profile})

@login_required
def saved_universities(request):
    saved = SavedUniversity.objects.filter(user=request.user)
    return render(request, 'universities/saved_universities.html', {'saved_universities': saved})

@login_required
@require_POST
def save_university(request, pk):
    try:
        university = get_object_or_404(University, id=pk)
        saved_item = SavedItems.objects.filter(
            user=request.user,
            item_type='UNIV',
            item_id=university.id
        ).first()
        
        if saved_item:
            saved_item.delete()
            messages.info(request, f'{university.name} has been removed from your saved list.')
        else:
            SavedItems.objects.create(
                user=request.user,
                item_type='UNIV',
                item_id=university.id,
                saved_date=timezone.now()
            )
            messages.success(request, f'{university.name} has been saved to your list.')
        
        return redirect('university_detail', pk=university.id)
    except Exception as e:
        messages.error(request, f'Error saving university: {str(e)}')
        return redirect('university_detail', pk=pk)

@login_required
def application_list(request):
    """View for listing user's applications."""
    try:
        with connection.cursor() as cursor:
            # Get applications with program details
            cursor.execute("""
                SELECT 
                    a.id,
                    a.created_at,
                    a.updated_at,
                    a.status,
                    a.start_term,
                    a.personal_statement,
                    u.name as university_name,
                    p.name as program_name,
                    p.id as program_id,
                    p.duration,
                    p.tuition as tuition_fee,
                    u.id as university_id
                FROM applications a
                JOIN university u ON a.university_id = u.id
                JOIN program p ON a.program_id = p.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            """, [request.user.id])
            applications = dictfetchall(cursor)

            # Get documents for each application
            for application in applications:
                cursor.execute("""
                    SELECT 
                        ud.document_type,
                        ud.file_path,
                        ud.original_filename,
                        ud.upload_date,
                        ud.document_status
                    FROM user_documents ud
                    WHERE ud.user_id = %s
                    ORDER BY ud.upload_date DESC
                """, [request.user.id])
                application['documents'] = dictfetchall(cursor)

            context = {
                'applications': applications,
                'can_apply': True
            }
            return render(request, 'applications/application_list.html', context)
    except Exception as e:
        print(f"Error in application_list: {str(e)}")
        messages.error(request, 'Error loading applications.')
        return render(request, 'applications/application_list.html', {'applications': []})

@login_required
def new_application(request, program_id):
    """View for creating a new application."""
    try:
        with connection.cursor() as cursor:
            # Get program details
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.university_id,
                    u.name as university_name
                FROM program p
                JOIN university u ON p.university_id = u.id
                WHERE p.id = %s
            """, [program_id])
            program = dictfetchone(cursor)

            if not program:
                messages.error(request, 'Program not found.')
                return redirect('program_list')

            # Get user's documents
            cursor.execute("""
                SELECT id, document_type, document_status
                FROM user_documents
                WHERE user_id = %s
            """, [request.user.id])
            user_documents = dictfetchall(cursor)

            # Map document types from upload form to application checklist
            document_type_mapping = {
                'passport': 'Passport',
                'diploma': 'Diploma',
                'transcript': 'Academic Transcripts',
                'resume': 'Resume',
                'language_test': 'Language Test Score',
                'standardized_test': 'Standardized Test Score',
                'recommendation': 'Recommendation Letter'
            }

            # Get list of document types with proper mapping
            user_documents_types = []
            for doc in user_documents:
                if doc['document_type'] in document_type_mapping:
                    user_documents_types.append(document_type_mapping[doc['document_type']])

            if request.method == 'POST':
                start_term = request.POST.get('start_term')
                personal_statement = request.POST.get('personal_statement')

                # Validate required fields
                if not start_term:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please select a start term.'
                        })
                    messages.error(request, 'Please select a start term.')
                    return render(request, 'applications/new_application.html', {
                        'program': program,
                        'user_documents': user_documents,
                        'user_documents_types': user_documents_types
                    })

                if not personal_statement:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Please provide a personal statement.'
                        })
                    messages.error(request, 'Please provide a personal statement.')
                    return render(request, 'applications/new_application.html', {
                        'program': program,
                        'user_documents': user_documents,
                        'user_documents_types': user_documents_types
                    })

                # Validate personal statement length (minimum 250 words)
                word_count = len(personal_statement.strip().split())
                if word_count < 250:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Personal statement must be at least 250 words.'
                        })
                    messages.error(request, 'Personal statement must be at least 250 words.')
                    return render(request, 'applications/new_application.html', {
                        'program': program,
                        'user_documents': user_documents,
                        'user_documents_types': user_documents_types
                    })

                # Check if user has all required documents
                if len(user_documents_types) < 7:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'You must upload all required documents before submitting an application.'
                        })
                    messages.error(request, 'You must upload all required documents before submitting an application.')
                    return render(request, 'applications/new_application.html', {
                        'program': program,
                        'user_documents': user_documents,
                        'user_documents_types': user_documents_types
                    })

                try:
                    # Start transaction
                    cursor.execute("START TRANSACTION")

                    # Check if user already has an application for this program and start term
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM applications 
                        WHERE user_id = %s 
                        AND program_id = %s 
                        AND start_term = %s
                        AND status != 'rejected'
                    """, [request.user.id, program_id, start_term])
                    result = cursor.fetchone()
                    existing_count = result[0] if result else 0

                    if existing_count > 0:
                        cursor.execute("ROLLBACK")
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'status': 'error',
                                'message': f'You already have an active application for this program for {start_term}. Please select a different term.'
                            })
                        messages.error(request, f'You already have an active application for this program for {start_term}. Please select a different term.')
                        return render(request, 'applications/new_application.html', {
                            'program': program,
                            'user_documents': user_documents,
                            'user_documents_types': user_documents_types
                        })

                    # Create new application
                    cursor.execute("""
                        INSERT INTO applications (
                            user_id, program_id, university_id, start_term, 
                            personal_statement, status, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, [
                        request.user.id,
                        program_id,
                        program['university_id'],
                        start_term,
                        personal_statement,
                        'pending'
                    ])

                    # Commit transaction
                    cursor.execute("COMMIT")

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'redirect': reverse('application_list')
                        })
                    messages.success(request, 'Application submitted successfully!')
                    return redirect('application_list')

                except Exception as e:
                    cursor.execute("ROLLBACK")
                    print(f"Error creating application: {str(e)}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Error submitting application. Please try again.'
                        })
                    messages.error(request, 'Error submitting application. Please try again.')
                    return render(request, 'applications/new_application.html', {
                        'program': program,
                        'user_documents': user_documents,
                        'user_documents_types': user_documents_types
                    })

            return render(request, 'applications/new_application.html', {
                'program': program,
                'user_documents': user_documents,
                'user_documents_types': user_documents_types
            })

    except Exception as e:
        print(f"Error in new_application: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Error creating application.'
            })
        messages.error(request, 'Error creating application.')
        return redirect('application_list')

@login_required
def application_detail(request, pk):
    """View for application details."""
    try:
        with connection.cursor() as cursor:
            # Get application details with program info
            cursor.execute("""
                SELECT 
                    a.id,
                    a.start_term,
                    a.personal_statement,
                    a.status,
                    a.created_at,
                    a.updated_at,
                    p.id as program_id,
                    p.name as program_name,
                    p.duration,
                    p.tuition as tuition_fee,
                    u.name as university_name,
                    u.id as university_id
                FROM applications a
                JOIN program p ON a.program_id = p.id
                JOIN university u ON p.university_id = u.id
                WHERE a.id = %s AND a.user_id = %s
            """, [pk, request.user.id])
            application = dictfetchone(cursor)

            if not application:
                messages.error(request, 'Application not found.')
                return redirect('application_list')

            # Get user's documents
            cursor.execute("""
                SELECT 
                    id,
                    document_type,
                    document_status,
                    file_path,
                    original_filename,
                    upload_date
                FROM user_documents
                WHERE user_id = %s
                ORDER BY upload_date DESC
            """, [request.user.id])
            user_documents = dictfetchall(cursor)

            context = {
                'application': application,
                'user_documents': user_documents
            }
            return render(request, 'applications/application_detail.html', context)
    except Exception as e:
        print(f"Error in application_detail: {str(e)}")
        messages.error(request, 'Error loading application details.')
        return redirect('application_list')

@login_required
def upload_documents(request):
    if request.method == 'POST':
        try:
            document_type = request.POST.get('document_type')
            document_file = request.FILES.get('document')
            
            if not document_type or not document_file:
                return JsonResponse({
                    'success': False,
                    'message': 'Document type and file are required'
                })
            
            # Create documents directory if it doesn't exist
            documents_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
            os.makedirs(documents_dir, exist_ok=True)
            
            # Generate a unique filename with user ID and timestamp
            timestamp = int(time.time())
            original_filename = document_file.name
            file_extension = original_filename.split('.')[-1].lower()
            
            # Create a safe filename
            safe_filename = f"user_{request.user.id}_{timestamp}_{document_type}.{file_extension}"
            
            # Full path for saving the file
            file_path = os.path.join(documents_dir, safe_filename)
            
            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in document_file.chunks():
                    destination.write(chunk)
            
            # Create relative path for database storage
            relative_path = os.path.join('documents', safe_filename)
            
            # Create document record
            document = UserDocuments.objects.create(
                user=request.user,
                document_type=document_type,
                file_path=relative_path,  # Store relative path
                original_filename=original_filename,
                document_status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Document uploaded successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all unread notifications as read."""
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({'status': 'error'}, status=500)

@login_required
def application_status(request):
    """View for checking application status."""
    applications = Application.objects.filter(user=request.user).select_related('program__university')
    return render(request, 'applications/status.html', {
        'applications': applications
    })

def program_search(request):
    """View for searching programs."""
    query = request.GET.get('q', '')
    degree = request.GET.get('degree')
    field = request.GET.get('field')
    
    programs = Program.objects.select_related('university', 'degree', 'field')
    
    if query:
        programs = programs.filter(
            Q(name__icontains=query) |
            Q(university__name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if degree:
        programs = programs.filter(degree__name=degree)
    
    if field:
        programs = programs.filter(field__name=field)
    
    return render(request, 'programs/search.html', {
        'programs': programs,
        'query': query,
        'degrees': Degree.objects.all(),
        'fields': Field.objects.all(),
        'selected_degree': degree,
        'selected_field': field,
    })

@login_required
def compare_universities(request):
    """View for comparing universities."""
    saved_universities = SavedUniversity.objects.filter(user=request.user).select_related(
        'university',
        'university__type',
        'university__universitystats',
        'university__universitydescription'
    )
    
    universities = [saved.university for saved in saved_universities]
    
    # Get programs for each university
    university_programs = {}
    for university in universities:
        programs = Program.objects.filter(university=university).select_related('degree', 'field')
        university_programs[university.id] = programs
    
    return render(request, 'universities/compare.html', {
        'universities': universities,
        'university_programs': university_programs,
    })

@login_required
def saved_items(request):
    """View to display saved universities and programs"""
    # Get saved items
    saved_items = SavedItems.objects.filter(user=request.user).order_by('-saved_date')
    
    # Separate universities and programs
    universities = []
    programs = []
    
    for item in saved_items:
        try:
            if item.item_type == 'uni':
                university = University.objects.get(id=item.item_id)
                universities.append({
                    'item': university,
                    'saved_date': item.saved_date,
                    'saved_id': item.id
                })
            else:
                program = Program.objects.get(id=item.item_id)
                programs.append({
                    'item': program,
                    'saved_date': item.saved_date,
                    'saved_id': item.id
                })
        except (University.DoesNotExist, Program.DoesNotExist):
            # If the university or program was deleted, remove the saved item
            item.delete()
            continue
    
    context = {
        'saved_universities': universities,
        'saved_programs': programs
    }
    return render(request, 'portal/saved_items.html', context)

@login_required
def save_item(request):
    """View to handle saving universities and programs"""
    if request.method == 'POST':
        try:
            item_type = request.POST.get('item_type')
            item_id = request.POST.get('item_id')
            
            if not item_type or not item_id:
                return JsonResponse({'error': 'Missing item type or ID'}, status=400)
            
            # Check if item exists
            if item_type == 'uni':
                item = get_object_or_404(University, id=item_id)
            else:
                item = get_object_or_404(Program, id=item_id)
            
            # Check if already saved
            existing = SavedItems.objects.filter(
                user=request.user,
                item_type=item_type,
                item_id=item_id
            ).first()
            
            if existing:
                return JsonResponse({'error': 'Item already saved'}, status=400)
            
            # Save the item
            SavedItems.objects.create(
                user=request.user,
                item_type=item_type,
                item_id=item_id
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Item saved successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
@require_POST
def remove_saved_item(request, item_id):
    try:
        with connection.cursor() as cursor:
            # First check if the item exists and belongs to the user
            cursor.execute("""
                SELECT item_type 
                FROM saved_items 
                WHERE id = %s AND user_id = %s
            """, [item_id, request.user.id])
            result = cursor.fetchone()
            
            if not result:
                return JsonResponse({
                    'success': False,
                    'message': 'Item not found'
                })
            
            # Delete the item
            cursor.execute("""
                DELETE FROM saved_items 
                WHERE id = %s AND user_id = %s
            """, [item_id, request.user.id])
            
            # Check if any rows were affected
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Item removed successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to remove item'
                })
    except Exception as e:
        print(f"Error removing saved item: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def delete_document(request, document_id):
    try:
        document = get_object_or_404(UserDocuments, id=document_id, user=request.user)
        file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error deleting file: {str(e)}'
                })
        
        document.delete()
        return JsonResponse({
            'success': True,
            'message': 'Document deleted successfully'
        })
    except UserDocuments.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Document not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def add_academic_record(request):
    if request.method == 'POST':
        try:
            academic_record = AcademicBackground.objects.create(
                user_id=request.user.id,
                school_name=request.POST.get('school_name'),
                level_completed=request.POST.get('level_completed'),
                field_of_study=request.POST.get('field_of_study'),
                start_year=request.POST.get('start_year'),
                completion_year=request.POST.get('completion_year'),
                result_type=request.POST.get('result_type'),
                result_value=request.POST.get('result_value'),
                additional_info=request.POST.get('additional_info'),
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            return JsonResponse({
                'success': True,
                'message': 'Academic record added successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
@require_POST
def delete_academic_record(request, record_id):
    try:
        record = AcademicBackground.objects.get(id=record_id, user=request.user)
        record.delete()
        return JsonResponse({
            'success': True,
            'message': 'Academic record deleted successfully'
        })
    except AcademicBackground.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Academic record not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def edit_academic_background(request, academic_id):
    """View to handle editing academic background"""
    try:
        academic = get_object_or_404(AcademicBackground, id=academic_id, user=request.user)
        
        if request.method == 'POST':
            academic.school_name = request.POST.get('school_name')
            academic.level_completed = request.POST.get('level_completed')
            academic.field_of_study = request.POST.get('field_of_study')
            academic.result_type = request.POST.get('result_type')
            academic.result_value = request.POST.get('result_value')
            academic.completion_year = request.POST.get('completion_year')
            academic.start_year = request.POST.get('start_year')
            academic.additional_info = request.POST.get('additional_info')
            academic.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Academic background updated successfully'
            })
        
        # Return academic background data for GET requests
        return JsonResponse({
            'success': True,
            'data': {
                'school_name': academic.school_name,
                'level_completed': academic.level_completed,
                'field_of_study': academic.field_of_study,
                'result_type': academic.result_type,
                'result_value': academic.result_value,
                'completion_year': academic.completion_year,
                'start_year': academic.start_year,
                'additional_info': academic.additional_info
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def delete_academic_background(request, academic_id):
    """View to handle deleting academic background"""
    if request.method == 'POST':
        try:
            academic = get_object_or_404(AcademicBackground, id=academic_id, user=request.user)
            academic.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Academic background deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)

@login_required
def get_academic_background(request, academic_id):
    """View to get academic background details"""
    try:
        academic = get_object_or_404(AcademicBackground, id=academic_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'school_name': academic.school_name,
                'level_completed': academic.level_completed,
                'field_of_study': academic.field_of_study,
                'result_type': academic.result_type,
                'result_value': academic.result_value,
                'completion_year': academic.completion_year,
                'start_year': academic.start_year,
                'additional_info': academic.additional_info
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_POST
def save_program(request, pk):
    try:
        program = get_object_or_404(Program, id=pk)
        saved_item = SavedItems.objects.filter(
            user=request.user,
            item_type='PROG',
            item_id=program.id
        ).first()
        
        if saved_item:
            saved_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'{program.name} has been removed from your saved programs.'
            })
        else:
            SavedItems.objects.create(
                user=request.user,
                item_type='PROG',
                item_id=program.id,
                saved_date=timezone.now()
            )
            return JsonResponse({
                'success': True,
                'message': f'{program.name} has been saved to your list.'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def submit_program_review(request, program_id):
    try:
        program = get_object_or_404(Program, id=program_id)
        
        # Get form data
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        graduation_year = request.POST.get('graduation_year')
        reviewer_name = request.POST.get('name')
        
        # Validate required fields
        if not all([rating, review_text, graduation_year, reviewer_name]):
            messages.error(request, 'All fields are required.')
            return redirect('program_detail', pk=program_id)
        
        # Validate rating (should be between 1 and 5)
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            messages.error(request, 'Rating must be between 1 and 5.')
            return redirect('program_detail', pk=program_id)
        
        # Check if user has already reviewed this program
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM program_reviews 
                WHERE program_id = %s AND name = %s
            """, [program_id, reviewer_name])
            existing_review = cursor.fetchone()
            
            if existing_review:
                messages.error(request, 'You have already reviewed this program.')
                return redirect('program_detail', pk=program_id)
            
            # Create the review
            cursor.execute("""
                INSERT INTO program_reviews 
                (program_id, rating, review, graduation_year, name, university_id, posted_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                program_id,
                rating,
                review_text,
                graduation_year,
                reviewer_name,
                program.university_id,
                timezone.now().date()
            ])
        
        messages.success(request, 'Your review has been submitted successfully.')
        return redirect('program_detail', pk=program_id)
        
    except Exception as e:
        print(f"Error submitting program review: {str(e)}")
        messages.error(request, 'Error submitting review. Please try again.')
        return redirect('program_detail', pk=program_id)

@login_required
@require_POST
def vote_review(request, review_id):
    try:
        is_helpful = request.POST.get('is_helpful') == 'true'
        
        with connection.cursor() as cursor:
            # Check if user has already voted
            cursor.execute("""
                SELECT id, is_helpful 
                FROM review_votes 
                WHERE review_id = %s AND user_id = %s
            """, [review_id, request.user.id])
            existing_vote = cursor.fetchone()
            
            if existing_vote:
                # Update existing vote
                if existing_vote[1] != is_helpful:
                    cursor.execute("""
                        UPDATE review_votes 
                        SET is_helpful = %s 
                        WHERE id = %s
                    """, [is_helpful, existing_vote[0]])
                    
                    # Update review vote counts
                    if is_helpful:
                        cursor.execute("""
                            UPDATE program_reviews 
                            SET helpful_votes = helpful_votes + 1,
                                not_helpful_votes = not_helpful_votes - 1
                            WHERE id = %s
                        """, [review_id])
                    else:
                        cursor.execute("""
                            UPDATE program_reviews 
                            SET helpful_votes = helpful_votes - 1,
                                not_helpful_votes = not_helpful_votes + 1
                            WHERE id = %s
                        """, [review_id])
            else:
                # Create new vote
                cursor.execute("""
                    INSERT INTO review_votes (review_id, user_id, is_helpful)
                    VALUES (%s, %s, %s)
                """, [review_id, request.user.id, is_helpful])
                
                # Update review vote counts
                if is_helpful:
                    cursor.execute("""
                        UPDATE program_reviews 
                        SET helpful_votes = helpful_votes + 1
                        WHERE id = %s
                    """, [review_id])
                else:
                    cursor.execute("""
                        UPDATE program_reviews 
                        SET not_helpful_votes = not_helpful_votes + 1
                        WHERE id = %s
                    """, [review_id])
        
        return JsonResponse({
            'success': True,
            'message': 'Vote recorded successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def delete_program_review(request, program_id, review_id):
    try:
        with connection.cursor() as cursor:
            # First check if the review exists and belongs to the user
            cursor.execute("""
                SELECT id, name 
                FROM program_reviews 
                WHERE id = %s
            """, [review_id])
            review = cursor.fetchone()
            
            if not review:
                messages.error(request, 'Review not found.')
                return redirect('program_detail', pk=program_id)
            
            # Check if the review belongs to the current user or user is staff
            if review[1] != request.user.get_full_name() and not request.user.is_staff:
                messages.error(request, 'You can only delete your own reviews.')
                return redirect('program_detail', pk=program_id)
            
            # Delete the review
            cursor.execute("""
                DELETE FROM program_reviews 
                WHERE id = %s
            """, [review_id])
            
            messages.success(request, 'Review deleted successfully.')
            return redirect('program_detail', pk=program_id)
            
    except Exception as e:
        messages.error(request, 'An error occurred while deleting the review.')
        return redirect('program_detail', pk=program_id)

@login_required
def moderate_review(request, review_id):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to moderate reviews.')
        return redirect('home')
        
    try:
        action = request.POST.get('action')
        if action not in ['approve', 'reject']:
            raise ValueError('Invalid action')
            
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE program_reviews 
                SET status = %s,
                    is_verified = %s
                WHERE id = %s
            """, [
                'approved' if action == 'approve' else 'rejected',
                action == 'approve',
                review_id
            ])
            
        messages.success(request, f'Review {action}d successfully.')
        return redirect('program_detail', pk=request.POST.get('program_id'))
        
    except Exception as e:
        messages.error(request, f'Error moderating review: {str(e)}')
        return redirect('home')

def unified_search(request):
    """View for unified search of universities and programs."""
    try:
        # Get search parameters
        search_query = request.GET.get('search', '').strip()
        country = request.GET.get('country', '').strip()
        uni_type = request.GET.get('type', '').strip()
        sort_by = request.GET.get('sort', 'ranking')

        with connection.cursor() as cursor:
            # Get filter options for the form
            cursor.execute("SELECT DISTINCT country FROM university WHERE country IS NOT NULL ORDER BY country")
            countries = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT id, type_name FROM university_type ORDER BY type_name")
            university_types = dictfetchall(cursor)

            # Base query for universities with all possible filters
            uni_query = """
                SELECT DISTINCT
                    u.id,
                    u.name,
                    u.location,
                    u.country,
                    u.world_university_ranking,
                    u.image_url,
                    u.two_line_info,
                    ut.type_name
                FROM university u
                LEFT JOIN university_type ut ON u.type_id = ut.id
                WHERE 1=1
            """
            uni_params = []

            # Base query for programs with all possible filters
            prog_query = """
                SELECT DISTINCT
                    p.id,
                    p.name,
                    u.location,
                    u.country,
                    p.tuition,
                    p.image_url,
                    p.program_overview as two_line_info,
                    d.name as type_name,
                    u.name as university_name
                FROM program p
                LEFT JOIN university u ON p.university_id = u.id
                LEFT JOIN university_type ut ON u.type_id = ut.id
                LEFT JOIN degree d ON p.degree_id = d.id
                WHERE 1=1
            """
            prog_params = []

            # Apply search filter if exists
            if search_query:
                uni_query += """ AND (
                    u.name LIKE %s OR 
                    u.location LIKE %s OR 
                    u.country LIKE %s OR
                    u.two_line_info LIKE %s
                )"""
                search_param = f"%{search_query}%"
                uni_params.extend([search_param, search_param, search_param, search_param])

                prog_query += """ AND (
                    p.name LIKE %s OR 
                    p.program_overview LIKE %s OR
                    u.name LIKE %s OR
                    d.name LIKE %s
                )"""
                prog_params.extend([search_param, search_param, search_param, search_param])

            # Apply country filter if exists
            if country:
                uni_query += " AND u.country = %s"
                uni_params.append(country)
                prog_query += " AND u.country = %s"
                prog_params.append(country)

            # Apply university type filter if exists
            if uni_type:
                uni_query += " AND ut.type_name = %s"
                uni_params.append(uni_type)
                # Also apply to programs through their university
                prog_query += " AND ut.type_name = %s"
                prog_params.append(uni_type)

            # Add sorting
            if sort_by == 'ranking':
                uni_query += " ORDER BY COALESCE(u.world_university_ranking, 999999) ASC"
                prog_query += " ORDER BY CASE WHEN p.tuition IS NULL THEN 1 ELSE 0 END, p.tuition"
            elif sort_by == 'name':
                uni_query += " ORDER BY u.name"
                prog_query += " ORDER BY p.name"
            elif sort_by == 'country':
                uni_query += " ORDER BY u.country"
                prog_query += " ORDER BY u.country"

            # Execute queries
            cursor.execute(uni_query, uni_params)
            universities = dictfetchall(cursor)

            cursor.execute(prog_query, prog_params)
            programs = dictfetchall(cursor)

            # Pagination for universities
            uni_paginator = Paginator(universities, 15)  # Changed to 15 items per page
            uni_page_number = request.GET.get('uni_page', 1)
            try:
                uni_page_number = int(uni_page_number)
                if uni_page_number < 1:
                    uni_page_number = 1
                elif uni_page_number > uni_paginator.num_pages:
                    uni_page_number = uni_paginator.num_pages
            except (ValueError, TypeError):
                uni_page_number = 1
            uni_page_obj = uni_paginator.page(uni_page_number)

            # Pagination for programs
            prog_paginator = Paginator(programs, 15)  # Changed to 15 items per page
            prog_page_number = request.GET.get('prog_page', 1)
            try:
                prog_page_number = int(prog_page_number)
                if prog_page_number < 1:
                    prog_page_number = 1
                elif prog_page_number > prog_paginator.num_pages:
                    prog_page_number = prog_paginator.num_pages
            except (ValueError, TypeError):
                prog_page_number = 1
            prog_page_obj = prog_paginator.page(prog_page_number)

            # Determine if we're showing filtered results
            has_filters = bool(country or uni_type)
            has_search = bool(search_query)
            show_all = not (has_search or has_filters)

            context = {
                'universities': uni_page_obj,
                'programs': prog_page_obj,
                'countries': countries,
                'university_types': university_types,
                'search_query': search_query,
                'selected_country': country,
                'selected_type': uni_type,
                'sort_by': sort_by,
                'has_search_query': has_search,
                'has_filters': has_filters,
                'show_all': show_all
            }
            return render(request, 'search_results.html', context)

    except Exception as e:
        print(f"Error in unified_search: {str(e)}")
        messages.error(request, 'Error performing search.')
        return render(request, 'search_results.html', {
            'universities': [],
            'programs': [],
            'countries': countries if 'countries' in locals() else [],
            'university_types': university_types if 'university_types' in locals() else [],
            'has_search_query': False,
            'has_filters': False,
            'show_all': True
        })

@login_required
def edit_application(request, pk):
    """View for editing an existing application."""
    try:
        with connection.cursor() as cursor:
            # Get application details with program info
            cursor.execute("""
                SELECT 
                    a.id,
                    a.start_term,
                    a.personal_statement,
                    a.status,
                    p.id as program_id,
                    p.name as program_name,
                    p.duration,
                    p.tuition as tuition_fee,
                    u.name as university_name
                FROM applications a
                JOIN program p ON a.program_id = p.id
                JOIN university u ON p.university_id = u.id
                WHERE a.id = %s AND a.user_id = %s
            """, [pk, request.user.id])
            application = dictfetchone(cursor)

            if not application:
                messages.error(request, 'Application not found.')
                return redirect('application_list')

            # Get user's documents
            cursor.execute("""
                SELECT 
                    id,
                    document_type,
                    document_status,
                    file_path,
                    original_filename,
                    upload_date
                FROM user_documents
                WHERE user_id = %s
                ORDER BY upload_date DESC
            """, [request.user.id])
            user_documents = dictfetchall(cursor)

            if request.method == 'POST':
                start_term = request.POST.get('start_term')
                personal_statement = request.POST.get('personal_statement')

                # Validate required fields
                if not all([start_term, personal_statement]):
                    messages.error(request, 'All fields are required.')
                    return render(request, 'applications/edit_application.html', {
                        'application': application,
                        'user_documents': user_documents
                    })

                # Update application
                cursor.execute("""
                    UPDATE applications
                    SET start_term = %s,
                        personal_statement = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND user_id = %s
                """, [start_term, personal_statement, pk, request.user.id])

                messages.success(request, 'Application updated successfully.')
                return redirect('application_detail', pk=pk)

            return render(request, 'applications/edit_application.html', {
                'application': application,
                'user_documents': user_documents
            })
    except Exception as e:
        print(f"Error in edit_application: {str(e)}")
        messages.error(request, 'Error updating application.')
        return redirect('application_list')

@login_required
def delete_application(request, pk):
    """View for deleting an application."""
    try:
        with connection.cursor() as cursor:
            # Check if application exists and belongs to user
            cursor.execute("""
                SELECT id FROM applications 
                WHERE id = %s AND user_id = %s
            """, [pk, request.user.id])
            
            if not cursor.fetchone():
                messages.error(request, 'Application not found.')
                return redirect('application_list')
            
            # Delete the application
            cursor.execute("""
                DELETE FROM applications 
                WHERE id = %s AND user_id = %s
            """, [pk, request.user.id])
            
            messages.success(request, 'Application deleted successfully.')
            return redirect('application_list')
            
    except Exception as e:
        print(f"Error in delete_application: {str(e)}")
        messages.error(request, 'Error deleting application.')
        return redirect('application_list')
