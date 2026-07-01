import io
from django.http import FileResponse
from gtts import gTTS
import json

def text_to_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            lang = data.get('lang', 'en-IN')
            
            if not text:
                return FileResponse(io.BytesIO(b""), status=400, content_type='audio/mp3')

            # Generate audio purely inside the server's RAM memory
            fp = io.BytesIO()
            tts = gTTS(text=text, lang=lang)
            tts.write_to_fp(fp)
            fp.seek(0) # Rewind the stream to the beginning
            
            # Stream the raw audio data bytes back directly to the website
            return FileResponse(fp, content_type='audio/mp3')
            
        except Exception as e:
            print("TTS Backend Error:", e)
            return FileResponse(io.BytesIO(b""), status=500, content_type='audio/mp3')
