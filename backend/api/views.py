from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import qrcode
from io import BytesIO
import base64


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
    """
    Get CSRF token for the frontend.
    """
    return Response({'csrfToken': get_token(request)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint that accepts username and password.
    Returns requires_mfa: true if user has MFA enabled.
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
            # Store user ID in session for MFA verification
            request.session['mfa_user_id'] = user.id
            request.session['mfa_authenticated'] = False
            return Response({
                'requires_mfa': True,
                'message': 'MFA verification required'
            }, status=status.HTTP_200_OK)
        else:
            request.session['mfa_user_id'] = user.id
            request.session['mfa_setup_required'] = True
            return Response({
                'requires_mfa_setup': True,
                'message': 'MFA setup required'
            }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_mfa(request):
    """
    Verify MFA token and complete login.
    """
    token = request.data.get('token')
    user_id = request.session.get('mfa_user_id')
    
    if not token or not user_id:
        return Response(
            {'error': 'Token and user ID are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        device = TOTPDevice.objects.get(user=user, confirmed=True)
        
        if device.verify_token(token):
            auth_login(request, user)
            request.session['mfa_authenticated'] = True
            del request.session['mfa_user_id']
            return Response({'message': 'MFA verified, login successful'}, status=status.HTTP_200_OK)
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
    Works with session-based user_id for initial setup.
    """
    if request.user.is_authenticated:
        user = request.user
    else:
        user_id = request.session.get('mfa_user_id')
        if not user_id:
            return Response(
                {'error': 'No user session found. Please login again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    device, created = TOTPDevice.objects.get_or_create(
        user=user,
        defaults={'name': 'some_device', 'confirmed': False}
    )
    
    if not device.confirmed:
        config_url = device.config_url
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
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def mfa_confirm(request):
    """
    Confirm MFA setup by verifying the token.
    Works with session-based user_id for initial setup.
    """
    token = request.data.get('token')
    
    if request.user.is_authenticated:
        user = request.user
    else:
        user_id = request.session.get('mfa_user_id')
        if not user_id:
            return Response(
                {'error': 'No user session found. Please login again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
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
            
            if request.session.get('mfa_setup_required'):
                auth_login(request, user)
                del request.session['mfa_setup_required']
                del request.session['mfa_user_id']
            
            return Response({'message': 'MFA setup confirmed'}, status=status.HTTP_200_OK)
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint that logs out the user and clears the session.
    """
    auth_logout(request)
    request.session.flush()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def welcome(request):
    """
    Welcome endpoint that returns success message for authenticated users.
    """
    return Response({'message': 'Success!'}, status=status.HTTP_200_OK)
