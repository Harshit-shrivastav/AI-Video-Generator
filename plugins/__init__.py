from .slide import generate_background_image, write_text_on_image
from .tiktok_tts import get_tt_tts
from .merge_vid import join_videos
from .imgtovid import merge_image_and_audio
from .elevenlabs_tts import get_elevenlabs_tts
from .edge_tts import get_edge_tts
from .model import get_llm_response


title = str(input("Please enter a title to get started")
llm_response = get_llm_response(title)

background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
written_text, extra_text = write_text_on_image(background_image, llm_response, "temps/slides/slide.png")

ask_tts = int(input("which tts service do you want to use\n1. ElevenLabs \n2. Edge\n3. TikTok")
              
if ask_tts == 1:
    pass
elif ask_tts == 2:
    get_edge_tts(written_text, "temps/voices/voice.mp3"):
elif ask_tts == 3 :
    get_tt_tts(written_text, "temps/voices/voice.mp3")

merge_image_and_audio(image_path, audio_path, output_path)
