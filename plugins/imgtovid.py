from moviepy.editor import AudioFileClip, ImageClip
import imageio
import tempfile
import os

def merge_image_and_audio(image_data, audio_data, fps=24):
    temp_image_path = None
    temp_audio_path = None
    temp_video_path = None

    try:
        # Save the image data to a temporary file
        temp_image_path = tempfile.mktemp(suffix=".png")
        with open(temp_image_path, "wb") as image_file:
            image_file.write(image_data)
        
        # Save the audio data to a temporary file
        temp_audio_path = tempfile.mktemp(suffix=".mp3")
        with open(temp_audio_path, "wb") as audio_file:
            audio_file.write(audio_data)

        # Load audio and image files
        audio = AudioFileClip(temp_audio_path)
        image = imageio.imread(temp_image_path)

        # Create the video clip with the image and set its duration and fps
        image_clip = ImageClip(image).set_duration(audio.duration).set_fps(fps)
        final_clip = image_clip.set_audio(audio)

        # Save the final video to a temporary file
        temp_video_path = tempfile.mktemp(suffix=".mp4")
        final_clip.write_videofile(temp_video_path, codec="libx264")

        # Read the video data from the temporary file
        with open(temp_video_path, "rb") as video_file:
            video_data = video_file.read()

        return video_data
    except Exception as e:
        print(f"Error merging image and audio: {e}")
        return None
    finally:
        # Clean up the temporary image, audio, and video files
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
