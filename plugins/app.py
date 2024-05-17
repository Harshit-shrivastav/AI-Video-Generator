from slide import generate_background_image, write_text_on_image
from tiktok_tts import get_tt_tts
from merge_vid import join_videos
from imgtovid import merge_image_and_audio
from elevenlabs_tts import get_elevenlabs_tts
from msedge_tts import get_edge_tts
from model import get_llm_response

title = str(input("Please enter a title to get started: "))
ask_tts = int(input("Which TTS service do you want to use?\n1. ElevenLabs \n2. Edge\n3. TikTok: "))
speaker = None
llm_response = None
voice = None

if ask_tts == 1 or ask_tts == 2:
    speaker = str(input("Enter a speaker name: "))
try:
    llm_response = get_llm_response(title)
except Exception as e:
    print(e)
if llm_response:
    print("LLM response fetched:", llm_response)
else:
    print("Failed to fetch LLM response. Exiting.")
    exit()

background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))

if background_image:
    print("Background image fetched")
else:
    print("Failed to generate background image. Exiting.")
    exit()

slide, extra_text, written_text = write_text_on_image(background_image, llm_response)

if slide:
    print("Slide fetched")
else:
    print("Failed to generate slide. Exiting.")
    exit()

videos = []

while extra_text: # Loop until no more extra text
    extra_text = None
    written_text = None
    slide = None
    voice = None
    vid = None
    if ask_tts == 1:
        voice = get_elevenlabs_tts(written_text, speaker)
    elif ask_tts == 2:
        voice = get_edge_tts(written_text)
    elif ask_tts == 3:
        try:
            voice = get_tt_tts(written_text)
            print("tt voice fetched")
        except Exception as e:
            print(e)
    try:
        if slide and voice:
            vid = merge_image_and_audio(slide, voice)
            print("img and aud merged")
        else:
            print("slide or voice missing")
    except Exception as e:
        print(e)
    if vid:
        print("Video merged")
        videos.append(vid)
    else:
        print("Failed to merge video. Skipping.")
    
    slide, written_text, extra_text = write_text_on_image(background_image, extra_text)

vid = merge_image_and_audio(slide, voice)

if vid:
    videos.append(vid)
    print("Final videos merged")
else:
    print("Failed to merge final video. Exiting.")
    exit()

join_videos(videos, "results/finalvideo.mp4")
print("Final video created successfully!")
