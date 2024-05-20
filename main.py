import os
import time
import smtplib
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from plugins.slide import generate_background_image, write_text_on_image
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

# Ensure the directory exists
os.makedirs("users/videos", exist_ok=True)

# Mount the directory for static serving
app.mount("/users", StaticFiles(directory="users"), name="users")

# SMTP Email Configuration
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_password"

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
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        traceback.print_exc()

def delete_file_after_24_hours(file_path: str):
    time.sleep(24 * 60 * 60)
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Failed to delete file: {e}")
        traceback.print_exc()

@app.post("/generate")
async def generate(
    title: str = Form(...), 
    speaker: str = Form(...), 
    email: str = Form(None), 
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        # Generate the response from the LLM
        llm_response = get_llm_response(title, """You are preparing educational slides for students. Ensure concepts are explained clearly and simply...""")
        
        # Generate the background image
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        
        # Write text on the image and prepare the slide
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        
        videos = []
        
        while extra_text:
            # Generate TTS for the text
            voice = await get_edge_tts(written_text, speaker)
            
            # Merge image and audio into a video
            if voice:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
                else:
                    print("Failed to merge video. Skipping.")
            
            # Prepare next slide if there's extra text
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
        
        # Final merge for remaining text
        voice = await get_edge_tts(written_text, speaker)
        if voice:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid:
                videos.append(final_vid)
            else:
                return JSONResponse(content={"error": "Failed to merge final video."}, status_code=500)
        
        # Prepare final video filename and path
        video_filename = f"{email.split('@')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        final_video_path = f"users/videos/{video_filename}"
        
        # Merge all video segments
        merge_videos(videos, final_video_path)
        
        # Schedule deletion of the video after 24 hours
        background_tasks.add_task(delete_file_after_24_hours, final_video_path)
        
        if email:
            video_link = f"http://your-domain.com/users/videos/{video_filename}"
            background_tasks.add_task(send_email, email, video_link)
        
        return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path}, status_code=200)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
