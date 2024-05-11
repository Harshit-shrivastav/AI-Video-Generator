from moviepy.editor import AudioFileClip, ImageClip
import imageio

def merge_image_and_audio(image_path, audio_path, fps=24):
    audio = AudioFileClip(audio_path)
    image = imageio.imread(image_path)
    image_clip = ImageClip(image).set_duration(audio.duration).set_fps(fps)
    final_clip = image_clip.set_audio(audio)
    return final_clip

# Example usage:
#final_video_clip = merge_image_and_audio("image.jpg", "audio.mp3")
#final_video_clip.preview()
