import requests
import base64

ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev'
TEXT_BYTE_LIMIT = 300

def get_tt_tts(text, speaker="en_us_001"):
    try:
        response = requests.post(f"{ENDPOINT}/api/generation", json={"text": text, "voice": speaker})
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                # Decode base64-encoded audio data
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
"""
try:
    text = "Hello, how are you?"
    output_file_path = "output_audio.mp3"

    audio_data = get_tt_tts(text)
    if audio_data:
        # Write audio data to a file
        with open(output_file_path, 'wb') as f:
            f.write(audio_data)
        print("Audio file saved successfully!")
    else:
        print("Failed to generate audio.")
except Exception as e:
    print(f"An error occurred: {e}")
"""
