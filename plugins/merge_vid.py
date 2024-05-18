def create_video(image, audio_data, save_path=None, fps=24):
    image_np = np.array(image)
    image_clip = ImageClip(image_np).set_fps(fps)
    audio_file = "temp_audio.mp3"
    with open(audio_file, "wb") as f:
        f.write(audio_data)
    audio_clip = AudioFileClip(audio_file)
    image_clip = image_clip.set_duration(audio_clip.duration)
    video = CompositeVideoClip([image_clip])
    video.audio = CompositeAudioClip([audio_clip])
    if save_path:
        video.write_videofile(save_path, codec='libx264', audio_codec='aac')
    else:
        video_buffer = BytesIO()
        video.write_videofile(video_buffer, codec='libx264', audio_codec='aac')
        video_data = video_buffer.getvalue()
        video_buffer.close()
        return video_data
    video.close()
    audio_clip.close()
    image_clip.close()
