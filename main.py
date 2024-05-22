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
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'Email_here')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'Password')

# System Prompt
slide_prompt = """You are preparing educational slides for students. Ensure concepts are explained clearly and simply, as if presenting directly to the students. Use bullet points for all information. Do not write paragraphs except for subjects like math where step-by-step explanations are necessary. For theoretical subjects, always use bullet points. Separate each point with '\n' to break the line and '\n\n' to beak the lines two times, means insert the space between lines and use (1,2,3...) or by (◈,☆,⇒,➱,➮➣,➢,☒,☑✔,✓,⊛,◉,⊙,⊛,⊚,‣,⁌,⁍,⦾,⦿) for bullet signs and make sure to insert bullet signs in starting of each point. For example:"1. This is the first point.\n2. This is another bullet point.\n\n3. And this is another with space between above line and so on."Do not include any instructions about subtitles, slide images, or point-by-point lists. The content provided should be detailed and ready for slide creation without additional formatting or instructions. Focus solely on the lesson content."""
exp_prompt = """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""

# Domain and port 
DOMAIN = os.environ.get('DOMAIN', 'http://127.0.0.1:8080')
PORT = os.environ.get('PORT', 8000)

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
        conversation_history = []
        
        # Initial LLM response
        user_input = title
        ai_response = get_llm_response(user_input, slide_prompt)
        conversation_history.append(f'user: {user_input}, ai: {ai_response}')
        
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        slide, extra_text, written_text = write_text_on_image(background_image, ai_response)
        videos = []
        
        while extra_text:
            # Prepare conversation history string
            conversation_str = '\n'.join(conversation_history)
            # Get TTS with the history included
            voice = await get_edge_tts(f"{conversation_str}\nuser: {written_text}", speaker)
            
            if voice:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
                else:
                    logger.warning("Failed to merge video. Skipping.")
            # Update history with new user and AI response
            ai_response = get_llm_response(written_text, exp_prompt)
            conversation_history.append(f'user: {written_text}, ai: {ai_response}')
            
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            slide, extra_text, written_text = write_text_on_image(background_image, ai_response)
        
        # Final voice synthesis with complete history
        conversation_str = '\n'.join(conversation_history)
        voice = await get_edge_tts(f"{conversation_str}\nuser: {written_text}", speaker)
        
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
        
        logger.info("Video generation completed successfully.")
        
        if email:
            video_link = f"{DOMAIN}/{final_video_path}"
            #background_tasks.add_task(send_email, email, video_link)
            try:
                send_email(email, video_link)
            except Exception as e:
                print("An error occurred in sending email:", e)
        return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path}, status_code=200)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
        if email:
            try:
                send_email(email, "An error occurred while generating your video file, please generate it again.")
            except Exception as e:
                print("An error occurred in sending email:", e)
        raise HTTPException(status_code=500, detail="An error occurred during video generation.")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
