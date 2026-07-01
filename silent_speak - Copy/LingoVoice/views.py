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
    """Renders the core workspace. FIXED template file name matching your repository."""
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
    Generates the audio file directly into the static directory and returns 
    the exact JSON response status your dashboard JavaScript expects.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request protocol style.'}, status=400)
    
    if gTTS is None:
        return JsonResponse({
            'status': 'error',
            'message': 'gTTS library not installed.'
        }, status=500)

    try:
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()
        incoming_lang = data.get('lang', 'en-IN')

        if not text_content:
            return JsonResponse({'status': 'error', 'message': 'Buffer string was parsed empty.'}, status=400)

        clean_lang = incoming_lang.split('-')[0]

        final_text = text_content
        if clean_lang != 'en' and GoogleTranslator is not None:
            try:
                final_text = GoogleTranslator(source='auto', target=clean_lang).translate(text_content)
            except Exception as e:
                print(f"Translation skip/fallback: {e}")

        # Construct the static folder path safely inside your asset tree
        output_directory = os.path.join(settings.BASE_DIR, 'LingoVoice', 'static', 'LingoVoice')
        os.makedirs(output_directory, exist_ok=True)
        output_file_path = os.path.join(output_directory, 'output.mp3')

        # Run compilation synthesis and save the audio file
        tts_engine = gTTS(text=final_text, lang=clean_lang, slow=False)
        tts_engine.save(output_file_path)

        # Return the exact JSON structure your original javascript looks for
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
