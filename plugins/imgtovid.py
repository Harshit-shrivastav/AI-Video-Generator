from moviepy.editor import AudioFileClip, ImageClip
import imageio

def merge_image_and_audio(image_path, audio_path, output_path, fps=24):
    audio = AudioFileClip(audio_path)
    image = imageio.imread(image_path)
    image_clip = ImageClip(image).set_duration(audio.duration).set_fps(fps)
    final_clip = image_clip.set_audio(audio)
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

