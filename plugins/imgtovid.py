from io import BytesIO
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
import tempfile
import os

def merge_image_and_audio(image, audio_data, fps=24, save_path=None):
    # Convert PIL image to numpy array
    image_np = np.array(image)

    # Load the image clip from numpy array
    image_clip = ImageClip(image_np).set_fps(fps)

    # Save audio data to a temporary file
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_file.write(audio_data)
    audio_file.close()

    # Create an audio clip from the audio file
    audio_clip = AudioFileClip(audio_file.name)

    # Set the duration of the image clip to match the audio
    image_clip = image_clip.set_duration(audio_clip.duration)

    # Combine the image and audio into a video clip
    video = CompositeVideoClip([image_clip])
    video.audio = CompositeAudioClip([audio_clip])

    if save_path:
        # Write the final video to the save path
        video.write_videofile(save_path, codec='libx264', audio_codec='aac')
        video_output = save_path
    else:
        # Write to a temporary file
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_path = temp_video_file.name
        video.write_videofile(temp_video_path, codec='libx264', audio_codec='aac')
        
        # Read the video data back as bytes
        with open(temp_video_path, "rb") as f:
            video_output = f.read()
        
        # Clean up temporary video file
        os.remove(temp_video_path)

    # Clean up audio file
    os.remove(audio_file.name)

    # Close the clips and file-like objects
    video.close()
    audio_clip.close()
    image_clip.close()

    return video_output
