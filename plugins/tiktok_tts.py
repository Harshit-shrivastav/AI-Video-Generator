import requests
import json
import base64

ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev'
TEXT_BYTE_LIMIT = 300

def generate_tts(text, speaker="en_us_001"):
    try:
        response = requests.post(f"{ENDPOINT}/api/generation", json={"text": text, "voice": speaker})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                # Decode base64-encoded audio data
                audio_data = base64.b64decode(data['data'])
                return audio_data, speaker
            else:
                print(f"Generation failed: {data.get('error', 'Unknown error')}")
                return None, None
        else:
            print(f"Failed to generate audio: {response.text}")
            return None, None
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None, None

def save_audio(audio_data):
    try:
        with open("audio.mp3", "wb") as f:
            f.write(audio_data)
        print("Audio saved successfully as 'audio.mp3'")
    except Exception as e:
        print(f"Error saving audio: {e}")


