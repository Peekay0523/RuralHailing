from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

@login_required
def tracking_preferences(request):
    """
    Display tracking preferences for logged-in users
    """
    if request.method == 'GET':
        return render(request, 'core/tracking_preferences.html')


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_tracking_preferences(request):
    """
    Update tracking preferences for logged-in users
    """
    try:
        data = json.loads(request.body)
        consent = data.get('tracking_consent', False)
        
        # Update user's tracking consent
        request.user.tracking_consent_given = consent
        if consent:
            request.user.tracking_consent_date = timezone.now()
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'tracking_consent': request.user.tracking_consent_given,
            'message': 'Tracking preferences updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating preferences: {str(e)}'
        }, status=400)

@login_required
def get_tracking_status(request):
    """
    Get the current tracking consent status for the user
    """
    return JsonResponse({
        'tracking_consent': request.user.tracking_consent_given,
        'tracking_consent_date': request.user.tracking_consent_date.isoformat() if request.user.tracking_consent_date else None
    })