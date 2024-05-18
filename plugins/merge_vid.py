import tempfile
import os
from io import BytesIO
from moviepy.editor import VideoFileClip, concatenate_videoclips

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
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_file.write(video_data)
        temp_video_file.close()
        video_clip = VideoFileClip(temp_video_file.name)
        video_clips.append(video_clip)
    final_clip = concatenate_videoclips(video_clips)
    final_clip.write_videofile(save_path, codec='libx264', audio_codec='aac')
    for clip in video_clips:
        clip.close()
        os.remove(clip.filename)
