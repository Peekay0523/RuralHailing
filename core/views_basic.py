from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@api_view(['GET'])
def api_status(request):
    return Response({'status': 'API is running'})