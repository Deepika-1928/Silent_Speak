from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
import json
import os

# Try importing dependencies dynamically
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


def home_view(request):
    """Renders the landing page."""
    return render(request, 'LingoVoice/home.html')


def register_view(request):
    """Handles new user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'LingoVoice/register.html', {'form': form})


def login_view(request):
    """Handles logging existing users into their dashboard session."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'LingoVoice/login.html', {'form': form})


def dashboard_view(request):
    """Renders the core multi-language communication workspace."""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'LingoVoice/dashboad.html')


def logout_view(request):
    """Logs out the user cleanly and returns them to the landing page."""
    logout(request)
    return redirect('home')


def text_to_speech(request):
    """
    Core Voice Engine:
    Receives text and a language code from the frontend, translates it, 
    saves it to the static folder, and returns a JSON success status
    so the frontend script can play the generated file perfectly.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request protocol style.'}, status=400)
    
    if gTTS is None:
        return JsonResponse({
            'status': 'error',
            'message': 'gTTS library not installed. Run "pip install gTTS" in your terminal.'
        }, status=500)

    try:
        # Load JSON payload from the frontend AJAX fetch request
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()
        incoming_lang = data.get('lang', 'en-IN')

        if not text_content:
            return JsonResponse({'status': 'error', 'message': 'Buffer string was parsed empty.'}, status=400)

        # Convert locale codes (e.g., 'ko-KR' -> 'ko', 'hi-IN' -> 'hi')
        clean_lang = incoming_lang.split('-')[0]

        # AUTOMATIC TRANSLATION LAYER
        final_text = text_content
        if clean_lang != 'en' and GoogleTranslator is not None:
            try:
                final_text = GoogleTranslator(source='auto', target=clean_lang).translate(text_content)
            except Exception as e:
                print(f"Translation skip/fallback: {e}")

        # Define the exact folder path your template expects: /static/LingoVoice/output.mp3
        static_dir = os.path.join(settings.BASE_DIR, 'LingoVoice', 'static', 'LingoVoice')
        os.makedirs(static_dir, exist_ok=True)
        output_filepath = os.path.join(static_dir, 'output.mp3')

        # Generate audio and save it directly to disk
        tts_engine = gTTS(text=final_text, lang=clean_lang, slow=False)
        tts_engine.save(output_filepath)
        
        # Return JSON success string matching your dashboard code expectations
        return JsonResponse({'status': 'success'})

    except Exception as error_log:
        return JsonResponse({'status': 'error', 'message': str(error_log)}, status=500)


@login_required
def feedback_view(request):
    """Handles displaying the feedback form page and logging data securely into SQLite."""
    if request.method == 'POST':
        msg_text = request.POST.get('message', '').strip()
        if msg_text:
            Feedback.objects.create(user=request.user, message=msg_text)
            messages.success(request, "Feedback submitted successfully!")
            return redirect('feedback')
    else:
        messages.error(request, "Message cannot be empty.")
            
    return render(request, 'LingoVoice/feedback.html')
