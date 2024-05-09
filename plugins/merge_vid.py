from moviepy.editor import VideoFileClip, concatenate_videoclips

def join_videos(video_paths, output_path):
    clips = [VideoFileClip(path) for path in video_paths]
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

