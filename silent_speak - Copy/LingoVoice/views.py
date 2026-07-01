from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
import json
import io

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

def home_view(request):
    return render(request, 'LingoVoice/home.html')

def register_view(request):
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
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'LingoVoice/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def text_to_speech(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)
        text_content = data.get('text', '').strip()
        incoming_lang = data.get('lang', 'en-IN')
        clean_lang = incoming_lang.split('-')[0]

        final_text = text_content
        if clean_lang != 'en' and GoogleTranslator is not None:
            try:
                final_text = GoogleTranslator(source='auto', target=clean_lang).translate(text_content)
            except: pass

        tts_engine = gTTS(text=final_text, lang=clean_lang, slow=False)
        audio_buffer = io.BytesIO()
        tts_engine.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Returning bytes directly as audio/mpeg
        return HttpResponse(audio_buffer.getvalue(), content_type="audio/mpeg")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def feedback_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        msg_text = data.get('message', '').strip()
        if msg_text:
            Feedback.objects.create(user=request.user, message=msg_text)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
