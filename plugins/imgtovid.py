from moviepy.editor import AudioFileClip, ImageClip
import imageio
import tempfile
import os

def merge_image_and_audio(image_path, audio_data, fps=24):
    try:
        temp_audio_path = tempfile.mktemp(suffix=".mp3")
        with open(temp_audio_path, "wb") as audio_file:
            audio_file.write(audio_data)
        audio = AudioFileClip(temp_audio_path)
        image = imageio.imread(image_path)
        image_clip = ImageClip(image).set_duration(audio.duration).set_fps(fps)
        final_clip = image_clip.set_audio(audio)
        temp_video_path = tempfile.mktemp(suffix=".mp4")
        final_clip.write_videofile(temp_video_path, codec="libx264")
        with open(temp_video_path, "rb") as video_file:
            video_data = video_file.read()
        
        return video_data
    except Exception as e:
        print(f"Error merging image and audio: {e}")
        return None
    finally:
        # Clean up the temporary audio and video files
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

"""
text = "Hello, this is a test."
speaker = "en_us_001"
audio_data = get_tt_tts(text, speaker)
if audio_data:
    video_data = merge_image_and_audio("path/to/image.jpg", audio_data)
    if video_data:
        # Do something with video_data, such as saving it to a file
        with open("output_video.mp4", "wb") as output_file:
            output_file.write(video_data)
        print("Video saved to output_video.mp4")
"""
