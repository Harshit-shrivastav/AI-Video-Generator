import requests
import base64

ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev'
TEXT_BYTE_LIMIT = 300

def get_tt_tts(text, output_file_path, speaker="en_us_001"):
    try:
        response = requests.post(f"{ENDPOINT}/api/generation", json={"text": text, "voice": speaker})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                # Decode base64-encoded audio data
                audio_data = base64.b64decode(data['data'])
                #save_audio(audio_data, output_file_path)
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

def save_audio(audio_data, output_file_path):
    try:
        with open(output_file_path, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved successfully as '{output_file_path}'")
    except Exception as e:
        print(f"Error saving audio: {e}")
