from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile
import os

def join_videos(video_datas, output_path):
    temp_video_paths = []
    try:
        for video_data in video_datas:
            temp_video_path = tempfile.mktemp(suffix=".mp4")
            with open(temp_video_path, "wb") as video_file:
                video_file.write(video_data)
            temp_video_paths.append(temp_video_path)
        clips = [VideoFileClip(path) for path in temp_video_paths]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        return output_path
    except Exception as e:
        print(f"Error joining videos: {e}")
        return None
    finally:
        # Clean up the temporary video files
        for path in temp_video_paths:
            if os.path.exists(path):
                os.remove(path)

"""
text = "Hello, this is a test."
speaker = "en_us_001"
video_data1 = merge_image_and_audio("path/to/image1.jpg", get_tt_tts(text, speaker))
video_data2 = merge_image_and_audio("path/to/image2.jpg", get_tt_tts("Another test", speaker))

if video_data1 and video_data2:
    video_datas = [video_data1, video_data2]
    output_video_path = join_videos(video_datas, "final_output_video.mp4")
    if output_video_path:
        print(f"Final video saved to: {output_video_path}")
"""
