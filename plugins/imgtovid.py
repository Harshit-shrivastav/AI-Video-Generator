from io import BytesIO
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
import tempfile
import os

def merge_image_and_audio(image, audio_data, fps=24, save_path=None):
    image_np = np.array(image)
    image_clip = ImageClip(image_np).set_fps(fps)
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_file.write(audio_data)
    audio_file.close()
    audio_clip = AudioFileClip(audio_file.name)
    image_clip = image_clip.set_duration(audio_clip.duration)
    video = CompositeVideoClip([image_clip])
    video.audio = CompositeAudioClip([audio_clip])

    if save_path:
        video.write_videofile(save_path, codec='libx264', audio_codec='aac')
        video_output = save_path
    else:
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_path = temp_video_file.name
        video.write_videofile(temp_video_path, codec='libx264', audio_codec='aac')
        
        with open(temp_video_path, "rb") as f:
            video_output = f.read()
        
        os.remove(temp_video_path)
    os.remove(audio_file.name)

    video.close()
    audio_clip.close()
    image_clip.close()

    return video_output
