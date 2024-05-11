from .slide import generate_background_image, write_text_on_image
from .tiktok_tts import get_tt_tts
from .merge_vid import join_videos
from .imgtovid import merge_image_and_audio
from .elevenlabs_tts import get_elevenlabs_tts
from .edge_tts import get_edge_tts
from .model import get_llm_response


title = str(input("Please a Enter a title to get started")
llm_response = get_llm_response(title)

background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
written_text, extra_text = write_text_on_image(background_image, '''this is another sentence''', "temps/slides/slide.png")

