from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .models import Note
import qrcode
from io import BytesIO
import base64
import urllib.parse
import os
from datetime import datetime
import hashlib
import time


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint that accepts username and password.
    Returns requires_mfa: true if user has MFA enabled.
    For MFA flow, returns a temporary token (user_id hash) that can be used for MFA verification.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Check if user has MFA enabled
        has_mfa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        
        if has_mfa:
            # Generate a temporary token for MFA verification
            # This is a simple hash of user_id + timestamp, valid for 5 minutes
            timestamp = int(time.time())
            temp_token_data = f"{user.id}:{timestamp}:{settings.SECRET_KEY}"
            temp_token = hashlib.sha256(temp_token_data.encode()).hexdigest()[:32]
            
            return Response({
                'requires_mfa': True,
                'message': 'MFA verification required',
                'temp_token': temp_token,
                'user_id': user.id,
                'timestamp': timestamp
            }, status=status.HTTP_200_OK)
        else:
            # Generate a temporary token for MFA setup
            timestamp = int(time.time())
            temp_token_data = f"{user.id}:{timestamp}:{settings.SECRET_KEY}"
            temp_token = hashlib.sha256(temp_token_data.encode()).hexdigest()[:32]
            
            return Response({
                'requires_mfa_setup': True,
                'message': 'MFA setup required',
                'temp_token': temp_token,
                'user_id': user.id,
                'timestamp': timestamp
            }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


def verify_temp_token(temp_token, user_id, timestamp):
    """
    Verify the temporary token used for MFA flow.
    Token is valid for 5 minutes.
    """
    current_time = int(time.time())
    if current_time - timestamp > 300:  # 5 minutes
        return False
    
    temp_token_data = f"{user_id}:{timestamp}:{settings.SECRET_KEY}"
    expected_token = hashlib.sha256(temp_token_data.encode()).hexdigest()[:32]
    return temp_token == expected_token


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_mfa(request):
    """
    Verify MFA token and complete login.
    Returns JWT tokens upon successful verification.
    """
    token = request.data.get('token')
    temp_token = request.data.get('temp_token')
    user_id = request.data.get('user_id')
    timestamp = request.data.get('timestamp')
    
    if not token or not temp_token or not user_id or not timestamp:
        return Response(
            {'error': 'Token, temp_token, user_id, and timestamp are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify temporary token
    try:
        user_id_int = int(user_id)
        timestamp_int = int(timestamp)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid user_id or timestamp format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not verify_temp_token(temp_token, user_id_int, timestamp_int):
        return Response(
            {'error': 'Invalid or expired temporary token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        user = User.objects.get(id=user_id_int)
        device = TOTPDevice.objects.get(user=user, confirmed=True)
        
        if device.verify_token(token):
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'MFA verified, login successful',
                **tokens
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid MFA token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except (User.DoesNotExist, TOTPDevice.DoesNotExist):
        return Response(
            {'error': 'MFA device not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def mfa_setup(request):
    """
    Get or create MFA device and return QR code for setup.
    Accepts temp_token, user_id, and timestamp for initial setup.
    """
    if request.user.is_authenticated:
        user = request.user
    else:
        # Get from query parameters (for initial setup)
        temp_token = request.GET.get('temp_token')
        user_id = request.GET.get('user_id')
        timestamp = request.GET.get('timestamp')
        
        if not temp_token or not user_id or not timestamp:
            return Response(
                {'error': 'temp_token, user_id, and timestamp are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify temporary token
        if not verify_temp_token(temp_token, int(user_id), int(timestamp)):
            return Response(
                {'error': 'Invalid or expired temporary token. Please login again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError):
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Create custom device name: "my-mfa-app + username"
    device_name = f"my-mfa-app-{user.username}"
    
    device, created = TOTPDevice.objects.get_or_create(
        user=user,
        defaults={'name': device_name, 'confirmed': False}
    )
    
    # Update device name if it was created with old name
    if device.name != device_name:
        device.name = device_name
        device.save()
    
    if not device.confirmed:
        base_config_url = device.config_url
        
        # Parse and customize the config URL
        # Extract secret from the original URL
        parsed = urllib.parse.urlparse(base_config_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        secret = query_params.get('secret', [device.key])[0]
        
        # Create custom config URL with "my-mfa-app" as issuer and username as account name
        issuer = "my-mfa-app"
        account_name = user.username
        config_url = f"otpauth://totp/{issuer}:{account_name}?secret={secret}&issuer={issuer}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(config_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'qr_code': f'data:image/png;base64,{qr_code_data}',
            'secret': device.key,
            'setup_required': True
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'setup_required': False,
            'message': 'MFA is already set up'
        }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def mfa_confirm(request):
    """
    Confirm MFA setup by verifying the token.
    Accepts temp_token, user_id, and timestamp for initial setup.
    Returns JWT tokens upon successful confirmation.
    """
    token = request.data.get('token')
    temp_token = request.data.get('temp_token')
    user_id = request.data.get('user_id')
    timestamp = request.data.get('timestamp')
    
    if request.user.is_authenticated:
        user = request.user
    else:
        if not temp_token or not user_id or not timestamp:
            return Response(
                {'error': 'temp_token, user_id, and timestamp are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify temporary token
        if not verify_temp_token(temp_token, int(user_id), int(timestamp)):
            return Response(
                {'error': 'Invalid or expired temporary token. Please login again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            user = User.objects.get(id=int(user_id))
        except (User.DoesNotExist, ValueError):
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        device = TOTPDevice.objects.get(user=user, confirmed=False)
        
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'MFA setup confirmed',
                **tokens
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except TOTPDevice.DoesNotExist:
        return Response(
            {'error': 'No pending MFA device found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint. With JWT, logout is handled client-side by removing tokens.
    Optionally, we can blacklist the refresh token here.
    """
    # In a production app, you might want to blacklist the refresh token
    # For now, we'll just return success - client should remove tokens
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def welcome(request):
    """
    Welcome endpoint that returns success message for authenticated users.
    """
    return Response({'message': 'Success!'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lucky_number(request):
    """
    Generate and return a random lucky number.
    """
    import random
    number = random.randint(1, 100)
    return Response({'number': number}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quote_of_the_day(request):
    """
    Return a random quote from a collection of quotes.
    """
    import random
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Don't let yesterday take up too much of today. - Will Rogers",
        "You learn more from failure than from success. - Unknown",
        "If you are working on something exciting that you really care about, you don't have to be pushed. The vision pulls you. - Steve Jobs",
        "People who are crazy enough to think they can change the world, are the ones who do. - Rob Siltanen"
    ]
    quote = random.choice(quotes)
    return Response({'quote': quote}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notes_list(request):
    """
    Get all notes for the authenticated user.
    """
    notes = Note.objects.filter(author=request.user)
    notes_data = []
    for note in notes:
        notes_data.append({
            'id': note.id,
            'title': note.title,
            'file_url': f'/api/notes/{note.id}/download/',  # Use API endpoint instead of direct file URL
            'file_path': note.file_path,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
        })
    return Response({'notes': notes_data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notes_create(request):
    """
    Create a new note and save it as a txt file.
    """
    title = request.data.get('title', '').strip()
    content = request.data.get('content', '').strip()
    
    if not title:
        return Response(
            {'error': 'Title is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not content:
        return Response(
            {'error': 'Content is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Ensure notes directory exists
    notes_dir = settings.NOTES_DIR
    os.makedirs(notes_dir, exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title.replace(' ', '_')[:50]
    filename = f"{request.user.id}_{timestamp}_{safe_title}.txt"
    file_path = os.path.join(notes_dir, filename)
    
    # Save content to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        return Response(
            {'error': f'Failed to save file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Create note record in database
    # Store relative path for the file
    relative_path = f'/media/notes/{filename}'
    note = Note.objects.create(
        author=request.user,
        title=title,
        file_path=relative_path
    )
    
    # Return API endpoint URL for downloading
    file_url = f'/api/notes/{note.id}/download/'
    
    return Response({
        'id': note.id,
        'title': note.title,
        'file_url': file_url,
        'created_at': note.created_at.isoformat(),
        'message': 'Note created successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notes_download(request, note_id):
    """
    Download a note file. Only the author can download their own notes.
    """
    try:
        note = Note.objects.get(id=note_id, author=request.user)
    except Note.DoesNotExist:
        return Response(
            {'error': 'Note not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get the actual file path
    file_path = os.path.join(settings.MEDIA_ROOT, note.file_path.lstrip('/media/'))
    
    if not os.path.exists(file_path):
        return Response(
            {'error': 'File not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Read and serve the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from django.http import HttpResponse
        
        # Sanitize filename for Content-Disposition header
        safe_filename = urllib.parse.quote(note.title.replace('/', '_').replace('\\', '_'))
        response = HttpResponse(content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}.txt"'
        return response
    except Exception as e:
        return Response(
            {'error': f'Failed to read file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notes_delete(request, note_id):
    """
    Delete a note and its associated txt file.
    """
    try:
        note = Note.objects.get(id=note_id, author=request.user)
    except Note.DoesNotExist:
        return Response(
            {'error': 'Note not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete the file
    file_path = os.path.join(settings.MEDIA_ROOT, note.file_path.lstrip('/media/'))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Warning: Failed to delete file {file_path}: {e}")
    
    # Delete the note record
    note.delete()
    
    return Response({'message': 'Note deleted successfully'}, status=status.HTTP_200_OK)
