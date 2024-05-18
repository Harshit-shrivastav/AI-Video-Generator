import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    concatenate_videoclips,
    VideoFileClip
)

def merge_videos(video_data_list, save_path):
    """
    Merges a list of video data into a single video.

    Args:
        video_data_list (list): List of video data in bytes.
        save_path (str): Path to save the final video.

    Returns:
        None
    """
    video_clips = []

    for video_data in video_data_list:
        video_buffer = BytesIO(video_data)
        video_clip = VideoFileClip(video_buffer)
        video_clips.append(video_clip)
    final_clip = concatenate_videoclips(video_clips)
    final_clip.write_videofile(save_path, codec='libx264', audio_codec='aac')
    for clip in video_clips:
        clip.close()
