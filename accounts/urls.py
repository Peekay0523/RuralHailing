from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterHTMLView.as_view(), name='register'),
    path('login/', views.LoginHTMLView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api-login'),
]

app_name = 'accounts'