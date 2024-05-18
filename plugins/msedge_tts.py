import asyncio
import random
import os
from concurrent.futures import ThreadPoolExecutor
import edge_tts
from edge_tts import VoicesManager

def get_edge_tts(text, output_file):
    async def async_generate_audio(text):
        try:
            voices = await VoicesManager.create()
            voice = voices.find(Locale="en-US")
            speaker = "en-US-MichelleNeural"
            communicate = edge_tts.Communicate(text, speaker)
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        except Exception as e:
            print("Error generating audio using edge_tts:", e)
            raise

    async def run_async(text):
        try:
            return await async_generate_audio(text)
        except Exception as e:
            print("An error occurred during audio generation:", e)
            raise

    try:
        return asyncio.run(run_async(text))
    except Exception as e:
        print("Error generating text to speech:", e)
        return None
