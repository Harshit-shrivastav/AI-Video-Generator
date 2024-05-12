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
if ask_tts == 1 or ask_tts == 2:
    speaker = str(input("Enter a speaker name: "))

llm_response = get_llm_response(title)
if llm_response:
    print("llm response fetched:", llm_response)
background_image = generate_background_image(1600, 900, (255, 255, 255), 10, (0, 0, 0))
if background_image:
    print("bkg img fetched")
slide, written_text, extra_text = write_text_on_image(background_image, llm_response)
if slide:
    print("slide fetched")

videos = []

if extra_text: # trying to do it recursive 
    voice = ''
    if ask_tts == 1:
        voice = get_elevenlabs_tts(written_text, speaker)
    elif ask_tts == 2:
        voice = get_edge_tts(written_text)
    elif ask_tts == 3:
        voice = get_tt_tts(written_text)

    vid = merge_image_and_audio(slide, voice)
    if vid:
        print("video merged")
    videos.append(vid)
    slide, written_text, extra_text = write_text_on_image(background_image, llm_response)
else:
    vid = merge_image_and_audio(slide, voice)
    videos.append(vid)

join_videos(videos, "results/finalvideo.mp4")
