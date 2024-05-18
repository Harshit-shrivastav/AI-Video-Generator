from slide import generate_background_image, write_text_on_image
from tiktok_tts import get_tt_tts
from merge_vid import merge_videos
from imgtovid import merge_image_and_audio
from elevenlabs_tts import get_elevenlabs_tts
from msedge_tts import get_edge_tts
from model import get_llm_response

title = input("Please enter a title to get started: ")
ask_tts = int(input("Which TTS service do you want to use?\n1. ElevenLabs \n2. Edge\n3. TikTok: "))
speaker = None
llm_response = None
voice = None

try:
    llm_response = get_llm_response(title)
except Exception as e:
    print("Failed to fetch LLM response:", e)
    exit()

background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
#background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
if not background_image:
    print("Failed to generate background image. Exiting.")
    exit()

slide = None
extra_text = None
written_text = None 
try:
    slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
except Exception as e:
    print("Error:", e)

if not slide or not written_text:
    print("Failed to generate slide or written text. Exiting.")
    exit()

print("Written text:", written_text)
print("Slide and written text fetched")

videos = []

while extra_text: 
    if ask_tts == 1:
        voice = get_elevenlabs_tts(written_text, speaker)
    elif ask_tts == 2:
        try:
            voice = get_edge_tts(written_text)
        except Exception as e:
            print('53', e)
    elif ask_tts == 3:
        try:
            voice = get_tt_tts(written_text)
        except Exception as e:
            print("Failed to fetch TikTok voice:", e)
            voice = None

    if voice:
        vid = merge_image_and_audio(slide, voice)
        if vid:
            print("Video merged")
            videos.append(vid)
        else:
            print("Failed to merge video. Skipping.")
    else:
        print("Slide or voice missing. Skipping.")

   # background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
    background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))

    try:
        slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
    except Exception as e:
        print("Error:", e)

    if not extra_text:
        break

    print("Written text:", written_text)
    print("Extra text:", extra_text)

if slide and voice:
    final_vid = merge_image_and_audio(slide, voice)
    if final_vid:
        videos.append(final_vid)
        print("Final video merged")
    else:
        print("Failed to merge final video. Exiting.")
        exit()
else:
    print("Slide or voice missing for final video. Exiting.")
    exit()

merge_videos(videos, "finalvideo.mp4")
print("Final video created successfully!")
