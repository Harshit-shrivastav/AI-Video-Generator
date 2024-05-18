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

try:
    llm_response = get_llm_response(title, "You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.")
except Exception as e:
    print("Failed to fetch LLM response:", e)
    exit()

background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
if not background_image:
    print("Failed to generate background image. Exiting.")
    exit()

slide = None
extra_text = None
written_text = None 
try:
    slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
except Exception as e:
    print("Error writing text on image:", e)
    exit()

if not slide or not written_text:
    print("Failed to generate slide or written text. Exiting.")
    exit()

print("Written text:", written_text)
print("Slide and written text fetched")

videos = []

while extra_text:
    voice = None
    try:
        if ask_tts == 1:
            voice = get_elevenlabs_tts(get_llm_response(written_text, ""), speaker)
        elif ask_tts == 2:
            voice = get_edge_tts(get_llm_response(written_text, ""))
            if not voice:
                print("Failed to get Edge TTS voice")
        elif ask_tts == 3:
            voice = get_tt_tts(get_llm_response(written_text, ""))
            if not voice:
                print("Failed to get TikTok TTS voice")
    except Exception as e:
        print(f"Failed to fetch TTS voice: {e}")

    if voice:
        try:
            vid = merge_image_and_audio(slide, voice)
            if vid:
                print("Video merged")
                videos.append(vid)
            else:
                print("Failed to merge video. Skipping.")
        except Exception as e:
            print(f"Error merging image and audio: {e}")
    else:
        print("Voice missing. Skipping.")

    # Refresh the background image for the next extra_text generation
    background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
    try:
        slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
    except Exception as e:
        print("Error writing text on image:", e)
        break

    if not extra_text:
        break

    print("Written text:", written_text)
    print("Extra text:", extra_text)

# Ensure voice is defined for the final slide
voice = None
try:
    if ask_tts == 1:
        voice = get_elevenlabs_tts(get_llm_response(written_text, ""), speaker)
    elif ask_tts == 2:
        voice = get_edge_tts(get_llm_response(written_text, ""))
        if not voice:
            print("Failed to get Edge TTS voice")
    elif ask_tts == 3:
        voice = get_tt_tts(get_llm_response(written_text, ""))
        if not voice:
            print("Failed to get TikTok TTS voice")
except Exception as e:
    print(f"Failed to fetch TTS voice: {e}")

if voice:
    try:
        final_vid = merge_image_and_audio(slide, voice)
        if final_vid:
            videos.append(final_vid)
            print("Final video merged")
        else:
            print("Failed to merge final video. Exiting.")
            exit()
    except Exception as e:
        print(f"Error merging final video: {e}")
        exit()
else:
    print("Voice missing for final video. Exiting.")
    exit()

try:
    merge_videos(videos, "finalvideo.mp4")
    print("Final video created successfully!")
except Exception as e:
    print(f"Failed to merge videos: {e}")
    exit()
