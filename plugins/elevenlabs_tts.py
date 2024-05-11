from elevenlabs import play
from elevenlabs.client import ElevenLabs
import os

API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def get_elevenlabs_tts(Text , Voice):
    if "ELEVENLABS_API_KEY" in os.environ:
        client = ElevenLabs(api_key=API_KEY)
        audio = client.generate(text=Text, voice = Voice, model="eleven_multilingual_v2")
        return audio 
    else:
        print("ElevenLabs API KEY is not available in environment")
        return False 
