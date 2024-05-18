import requests
import base64
import asyncio 

ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev'
TEXT_BYTE_LIMIT = 300

async def get_tt_tts(text, speaker="en_us_001"):
    try:
        response = requests.post(f"{ENDPOINT}/api/generation", json={"text": text, "voice": speaker})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                audio_data = base64.b64decode(data['data'])
                return audio_data
            else:
                print(f"Generation failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"Failed to generate audio: {response.text}")
            return None
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
