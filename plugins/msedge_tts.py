import asyncio
import random
import os
from concurrent.futures import ThreadPoolExecutor
import edge_tts
from edge_tts import VoicesManager

async def get_edge_tts(text: str, speaker: str) -> bytes:
    async def async_generate_audio(text: str, speaker: str) -> bytes:
        try:
            communicate = edge_tts.Communicate(text, speaker)
            audio_data = b''
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        except Exception as e:
            print("Error generating audio using edge_tts:", e)
            raise

    try:
        return await async_generate_audio(text, speaker)
    except Exception as e:
        print("An error occurred during audio generation:", e)
        return None
