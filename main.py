import os
import time
import smtplib
import traceback
import hashlib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from fastapi import FastAPI, Form, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging

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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        traceback.print_exc()

def delete_file_after_24_hours(file_path: str):
    time.sleep(24 * 60 * 60)
    try:
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        traceback.print_exc()

@app.post("/generate")
async def generate(
    background_tasks: BackgroundTasks,
    title: str = Form(...), 
    speaker: str = Form(...),
    email: Optional[str] = Form(None)
):
    try:
        logger.info("Generating video started.")
        llm_response = get_llm_response(title, """You are preparing educational slides for students. Ensure concepts are explained clearly and simply...""")
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        videos = []
        
        while extra_text:
            voice = await get_edge_tts(written_text, speaker)
            if voice:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
                else:
                    logger.warning("Failed to merge video. Skipping.")
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
        
        voice = await get_edge_tts(written_text, speaker)
        if voice:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid:
                videos.append(final_vid)
            else:
                raise HTTPException(status_code=500, detail="Failed to merge final video.")
        
        hash_input = f"{title}{datetime.now().timestamp()}".encode()
        video_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(hash_input).hexdigest()}.mp4"
        final_video_path = f"users/videos/{video_filename}"
        merge_videos(videos, final_video_path)
        
        background_tasks.add_task(delete_file_after_24_hours, final_video_path)
        
        if email:
            video_link = f"http://your-domain.com/{final_video_path}"
            background_tasks.add_task(send_email, email, video_link)
        
        logger.info("Video generation completed successfully.")
        return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path}, status_code=200)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred during video generation.")

@app.post("/update-email")
async def update_email(request: Request):
    try:
        data = await request.json()
        email = data.get('email')
        video_path = data.get('video_path')
        if not email or not video_path:
            raise HTTPException(status_code=400, detail="Email and video path are required.")
        
        video_link = f"http://your-domain.com/{video_path}"
        
        send_email(email, video_link)
        
        return JSONResponse(content={"message": "Email updated and notification sent successfully."}, status_code=200)
    except Exception as e:
        logger.error(f"An error occurred while updating email: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred while updating email.")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
