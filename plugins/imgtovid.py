from moviepy.editor import AudioFileClip, ImageClip
import imageio
import tempfile
import os

def merge_image_and_audio(image_path, audio_data, fps=24):
    temp_video_path = None
    temp_audio_path = None
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
