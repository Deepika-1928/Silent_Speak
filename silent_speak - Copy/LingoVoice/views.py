import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from gtts import gTTS

def home_view(request):
    """
    Renders the workspace dashboard console.
    """
    return render(request, 'LingoVoice/dashboad.html')


def text_to_speech(request):
    """
    Handles the vocal synthesis request. Generates an MP3 file in the static directory
    and returns a success JSON status so the frontend JavaScript plays it perfectly.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '').strip()
            lang = data.get('lang', 'en-IN')
            
            if not text:
                return JsonResponse({'status': 'error', 'message': 'Text context stream is empty.'}, status=400)

            # Define static file path where your frontend expects it
            static_dir = os.path.join(settings.BASE_DIR, 'LingoVoice', 'static', 'LingoVoice')
            os.makedirs(static_dir, exist_ok=True)
            output_filepath = os.path.join(static_dir, 'output.mp3')

            # Generate and save the audio file
            tts = gTTS(text=text, lang=lang)
            tts.save(output_filepath)
            
            # Return JSON status exactly matching what your dashboard JavaScript expects
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print("TTS Backend Exception raised:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def feedback_view(request):
    """
    Receives feedback messages securely via JSON POST requests and 
    saves them directly to your backend log / database.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'status': 'error', 'error': 'Feedback text content cannot be blank.'}, status=400)
            
            print(f"Feedback successfully received: {message}")
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'error': 'Invalid request method.'}, status=405)
