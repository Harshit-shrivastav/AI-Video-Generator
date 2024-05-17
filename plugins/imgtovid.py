from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, concatenate_videoclips
import imageio
import tempfile
import os

def merge_image_and_audio(image_path, audio_data, fps=24):
    temp_audio_path = None
    temp_video_path = None
    
    try:
        # Save the audio data to a temporary file
        temp_audio_path = tempfile.mktemp(suffix=".mp3")
        with open(temp_audio_path, "wb") as audio_file:
            audio_file.write(audio_data)
        
        # Read the image and create an ImageClip
        audio = AudioFileClip(temp_audio_path)
        image = imageio.imread(image_path)  # Read image as numpy array
        image_clip = ImageClip(image).set_duration(audio.duration).set_fps(fps)  # Use numpy array
        
        # Set the audio of the ImageClip
        final_clip = image_clip.set_audio(audio)
        
        # Save the final video to a temporary file
        temp_video_path = tempfile.mktemp(suffix=".mp4")
        final_clip.write_videofile(temp_video_path, codec="libx264", audio_codec="aac")
        
        # Read the video file back into memory
        with open(temp_video_path, "rb") as video_file:
            video_data = video_file.read()
        
        return video_data
    except Exception as e:
        print(f"Error merging image and audio: {e}")
        return None
    finally:
        # Clean up the temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        # Clean up the temporary video file only if it was created
        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
