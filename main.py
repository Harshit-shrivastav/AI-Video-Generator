from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import traceback
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List
import threading
import time

from plugins.slide import generate_background_image, write_text_on_image
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

# Ensure the directory exists
os.makedirs("root/users/videos", exist_ok=True)

app.mount("/users", StaticFiles(directory="root/users"), name="users")
app.mount("/static", StaticFiles(directory="root/static"), name="static")

EMAIL_ADDRESS = "
EMAIL_PASSWORD = "

def send_email(email: str, video_link: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = 'Your Video Download Link'
        
        body = f'Your video is ready! You can download it from the following link: {video_link}\nNote: The link will be valid for 24 hours.'
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def delete_file_after_24_hours(file_path: str):
    time.sleep(24 * 60 * 60)
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Failed to delete file: {e}")

@app.post("/generate")
async def generate(
    title: str = Form(...), 
    speaker: str = Form(...), 
    email: str = Form(...), 
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        llm_response = get_llm_response(title, """You are preparing educational slides for students. Ensure concepts are explained clearly and simply...""")
    except Exception as e:
        error_message = f"Failed to fetch LLM response: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    try:
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        if not background_image:
            raise ValueError("Failed to generate background image.")
    except Exception as e:
        error_message = f"Error generating background image: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    try:
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        if not slide or not written_text:
            raise ValueError("Failed to generate slide or written text.")
    except Exception as e:
        error_message = f"Error writing text on image: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    videos = []

    while extra_text:
        try:
            voice = await get_edge_tts(written_text, speaker)
        except Exception as e:
            error_message = f"Error generating TTS: {e}"
            print(error_message)
            print(traceback.format_exc())
            return JSONResponse(content={"error": error_message}, status_code=500)

        if voice:
            try:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    print("Video merged")
                    videos.append(vid)
                else:
                    print("Failed to merge video. Skipping.")
            except Exception as e:
                error_message = f"Error merging image and audio: {e}"
                print(error_message)
                print(traceback.format_exc())
                return JSONResponse(content={"error": error_message}, status_code=500)
        else:
            print("Voice missing. Skipping.")

        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        try:
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
        except Exception as e:
            error_message = f"Error writing text on image: {e}"
            print(error_message)
            print(traceback.format_exc())
            break

        if not extra_text:
            break

    voice = None
    try:
        voice = await get_edge_tts(written_text, speaker)
    except Exception as e:
        error_message = f"Failed to fetch TTS voice: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    if voice:
        try:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid:
                videos.append(final_vid)
                print("Final video merged")
                # Update progress to 80%
                return JSONResponse(content={"message": "Final video merged", "step": "final_video_merged"}, status_code=200)
            else:
                print("Failed to merge final video. Exiting.")
                return JSONResponse(content={"error": "Failed to merge final video."}, status_code=500)
        except Exception as e:
            error_message = f"Error merging final video: {e}"
            print(error_message)
            print(traceback.format_exc())
            return JSONResponse(content={"error": error_message}, status_code=500)
    else:
        print("Voice missing for final video. Exiting.")
        return JSONResponse(content={"error": "Voice missing for final video."}, status_code=500)

    video_filename = f"{email.split('@')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    final_video_path = f"root/users/videos/{video_filename}"

    try:
        merge_videos(videos, final_video_path)
        print("Final video created successfully!")
        background_tasks.add_task(delete_file_after_24_hours, final_video_path)
        
        if email:
            video_link = f"http://your-domain.com/users/videos/{video_filename}"
            background_tasks.add_task(send_email, email, video_link)

        return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path, "step": "video_ready"}, status_code=200)
    except Exception as e:
        error_message = f"Failed to merge videos: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

@app.get("/")
async def root():
    return FileResponse("root/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
