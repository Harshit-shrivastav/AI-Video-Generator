from slide import generate_background_image, write_text_on_image
from tiktok_tts import get_tt_tts
from merge_vid import join_videos
from imgtovid import merge_image_and_audio
from elevenlabs_tts import get_elevenlabs_tts
from msedge_tts import get_edge_tts
from model import get_llm_response

title = input("Please enter a title to get started: ")
ask_tts = int(input("Which TTS service do you want to use?\n1. ElevenLabs \n2. Edge\n3. TikTok: "))
speaker = None
llm_response = None
voice = None

if ask_tts == 1 or ask_tts == 2:
    speaker = input("Enter a speaker name: ")

try:
    llm_response = get_llm_response(title)
    print("LLM response fetched:", llm_response)
except Exception as e:
    print("Failed to fetch LLM response:", e)
    exit()

background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
if background_image:
    print("Background image fetched")
else:
    print("Failed to generate background image. Exiting.")
    exit()

slide, written_text, extra_text = write_text_on_image(background_image, llm_response)
if slide and written_text:
    print("Slide and written text fetched")
else:
    print("Failed to generate slide or written text. Exiting.")
    exit()

videos = []

while extra_text: 
    voice = None
    if ask_tts == 1:
        voice = get_elevenlabs_tts(written_text, speaker)
    elif ask_tts == 2:
        voice = get_edge_tts(written_text)
    elif ask_tts == 3:
        try:
            voice = get_tt_tts(written_text)
            print("TikTok voice fetched")
        except Exception as e:
            print("Failed to fetch TikTok voice:", e)
    
    if slide and voice:
        vid = merge_image_and_audio(slide, voice)
        if vid:
            print("Video merged")
            videos.append(vid)
        else:
            print("Failed to merge video. Skipping.")
    else:
        print("Slide or voice missing. Skipping.")

    slide, written_text, extra_text = write_text_on_image(background_image, extra_text)

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

join_videos(videos, "results/finalvideo.mp4")
print("Final video created successfully!")
