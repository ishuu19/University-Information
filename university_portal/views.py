from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction, connection
from .models import UserProfile, AcademicBackground, UserDocument, SavedItem
from .forms import AcademicBackgroundForm
import os
from django.conf import settings
from datetime import datetime
import traceback

@login_required
def profile_view(request):
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

        # Get saved items
        cursor.execute("""
            SELECT 
                id,
                item_type,
                item_id,
                saved_date
            FROM saved_items
            WHERE user_id = %s
            ORDER BY saved_date DESC
        """, [request.user.id])
        saved_items = cursor.fetchall()

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

    # Convert saved items to list of dictionaries
    saved_items_data = []
    for item in saved_items:
        saved_items_data.append({
            'id': item[0],
            'item_type': item[1],
            'item_id': item[2],
            'saved_date': item[3]
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
        'saved_items': saved_items_data,
        'applications': application_data
    }

    return render(request, 'registration/profile.html', context)

@login_required
def add_academic_background(request):
    if request.method == 'POST':
        form = AcademicBackgroundForm(request.POST)
        if form.is_valid():
            try:
                academic = form.save(commit=False)
                academic.user = request.user
                academic.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Update auth_user table
                cursor.execute("""
                    UPDATE auth_user 
                    SET first_name = %s,
                        last_name = %s,
                        email = %s
                    WHERE id = %s
                """, [
                    request.POST.get('first_name', ''),
                    request.POST.get('last_name', ''),
                    request.POST.get('email', ''),
                    request.user.id
                ])

                # Check if user profile exists
                cursor.execute("""
                    SELECT id FROM user_profiles 
                    WHERE user_id = %s
                """, [request.user.id])
                profile = cursor.fetchone()

                if profile:
                    # Update existing profile (remove first_name and last_name)
                    cursor.execute("""
                        UPDATE user_profiles 
                        SET phone = %s,
                            address = %s,
                            bio = %s
                        WHERE user_id = %s
                    """, [
                        request.POST.get('phone', ''),
                        request.POST.get('address', ''),
                        request.POST.get('bio', ''),
                        request.user.id
                    ])
                else:
                    # Create new profile (remove first_name and last_name)
                    cursor.execute("""
                        INSERT INTO user_profiles 
                        (user_id, phone, address, bio)
                        VALUES (%s, %s, %s, %s)
                    """, [
                        request.user.id,
                        request.POST.get('phone', ''),
                        request.POST.get('address', ''),
                        request.POST.get('bio', '')
                    ])

                # Handle profile image upload
                if 'photo' in request.FILES:
                    photo = request.FILES['photo']
                    # Validate file type
                    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
                    if photo.content_type not in allowed_types:
                        return JsonResponse({'success': False, 'error': 'Invalid file type. Please upload JPG, PNG, or GIF.'})
                    # Validate file size (max 5MB)
                    if photo.size > 5 * 1024 * 1024:
                        return JsonResponse({'success': False, 'error': 'File size too large. Maximum size is 5MB.'})
                    # Save the file to MEDIA_ROOT/profile_photos with a unique name
                    photos_dir = os.path.join(settings.MEDIA_ROOT, 'profile_photos')
                    os.makedirs(photos_dir, exist_ok=True)
                    ext = photo.name.split('.')[-1]
                    filename = f"user_{request.user.id}_{int(datetime.now().timestamp())}.{ext}"
                    file_path = os.path.join(photos_dir, filename)
                    with open(file_path, 'wb+') as destination:
                        for chunk in photo.chunks():
                            destination.write(chunk)
                    # Store the relative path in the database
                    relative_path = os.path.join('profile_photos', filename)
                    cursor.execute("""
                        UPDATE user_profiles 
                        SET image_url = %s
                        WHERE user_id = %s
                    """, [relative_path, request.user.id])
            return JsonResponse({'success': True})
        except Exception as e:
            print("Error uploading profile photo:", e)
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def upload_document(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            document = request.FILES['document']
            document_type = request.POST.get('document_type')
            notes = request.POST.get('notes', '')
            
            # Validate document type
            valid_types = ['diploma', 'transcript', 'resume', 'passport', 'standardized_test', 
                         'language_test', 'recommendation', 'eca', 'other']
            if document_type not in valid_types:
                return JsonResponse({'success': False, 'error': 'Invalid document type'})
            
            # Generate a unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{request.user.id}_{timestamp}_{document.name}"
            
            # Create the relative path for database storage
            relative_path = os.path.join('documents', safe_filename)
            
            # Create the full path for file storage
            full_path = os.path.join(settings.MEDIA_ROOT, 'documents', safe_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save the file
            with open(full_path, 'wb+') as destination:
                for chunk in document.chunks():
                    destination.write(chunk)
            
            # Create document record with relative path
            UserDocument.objects.create(
                user=request.user,
                document_type=document_type,
                file_path=relative_path,  # Store relative path
                original_filename=document.name,
                notes=notes,
                document_status='pending'
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_document(request, doc_id):
    if request.method == 'POST':
        try:
            document = get_object_or_404(UserDocument, id=doc_id, user=request.user)
            
            # Delete the file
            if document.file_path:
                file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            document.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def unsave_item(request, item_id):
    if request.method == 'POST':
        try:
            saved_item = get_object_or_404(SavedItem, id=item_id, user=request.user)
            saved_item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def browse_courses(request):
    # Implement your course browsing logic here
    return render(request, 'courses/browse.html')

@login_required
def delete_academic_background(request, education_id):
    if request.method == 'POST':
        try:
            education = get_object_or_404(AcademicBackground, id=education_id, user=request.user)
            education.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}) 