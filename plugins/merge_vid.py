import tempfile
import os
import asyncio
from io import BytesIO
from moviepy.editor import VideoFileClip, concatenate_videoclips

async def merge_videos(video_data_list, save_path):
    if len(video_data_list) == 1:
        single_video_data = video_data_list[0]
        with open(save_path, 'wb') as f:
            f.write(single_video_data)
    else:
        video_clips = []
        temp_files = []
        try:
            for video_data in video_data_list:
                temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_video_file.write(video_data)
                temp_video_file.close()
                temp_files.append(temp_video_file.name)
                video_clip = VideoFileClip(temp_video_file.name)
                video_clips.append(video_clip)
            
            final_clip = concatenate_videoclips(video_clips)
            final_clip.write_videofile(save_path, codec='libx264', audio_codec='aac')
        finally:
            for clip in video_clips:
                clip.close()
            for temp_file in temp_files:
                os.remove(temp_file)
