from django.contrib import admin
from django.urls import path
from LingoVoice import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Flow Pages
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # Audio Processing Engine Path (Fixes your connection alert error)
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),

    # Feedback Flow Page
    path('feedback/', views.feedback_view, name='feedback'),
]

# Serves static sound files properly during local development testing
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)