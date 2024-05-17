from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips
import imageio
import tempfile
import os
from PIL import Image

def merge_image_and_audio(image_path, audio_data, fps=24):
    temp_video_path = None
    temp_audio_path = None
    try:
        # Convert RGBA image to RGB
        image = Image.open(image_path)
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Save the RGB image to a temporary file
        temp_image_path = tempfile.mktemp(suffix=".png")
        image.save(temp_image_path)

        # Save the audio data to a temporary file
        temp_audio_path = tempfile.mktemp(suffix=".mp3")
        with open(temp_audio_path, "wb") as audio_file:
            audio_file.write(audio_data)

        # Load audio and image clips
        audio = AudioFileClip(temp_audio_path)
        image_clip = ImageClip(temp_image_path).set_duration(audio.duration).set_fps(fps)

        # Merge image and audio clips
        final_clip = image_clip.set_audio(audio)

        # Write the merged video to a temporary file
        temp_video_path = tempfile.mktemp(suffix=".mp4")
        final_clip.write_videofile(temp_video_path, codec="libx264")

        # Read the merged video data
        with open(temp_video_path, "rb") as video_file:
            video_data = video_file.read()

        return video_data
    except Exception as e:
        print(f"Error merging image and audio: {e}")
        return None
    finally:
        # Clean up the temporary files
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

