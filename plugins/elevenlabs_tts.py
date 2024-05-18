from elevenlabs import play
from elevenlabs.client import ElevenLabs
import os
import asyncio 

API_KEY = os.environ.get("ELEVENLABS_API_KEY")

async def get_elevenlabs_tts(text, voice):
    if API_KEY:
        client = ElevenLabs(api_key=API_KEY)
        audio = client.generate(text=text, voice=voice, model="eleven_multilingual_v2")
        return audio
    else:
        print("ElevenLabs API KEY is not available in environment")
        return None
