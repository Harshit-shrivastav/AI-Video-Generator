import traceback
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import List
import asyncio

from plugins.slide import generate_background_image, write_text_on_image
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.elevenlabs_tts import get_elevenlabs_tts
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

#slide_prompt = """You are preparing educational slides for students. Ensure concepts are explained clearly and simply, as if presenting directly to the students. Use bullet points for all information. Do not write paragraphs except for subjects like math where step-by-step explanations are necessary. For theoretical subjects, always use bullet points. Separate each point with '\n' to break the line and '\n\n' to beak the lines two times, means insert the space between lines and use (1,2,3...) or by '*' for bullet signs add make sure to insert bullet signs in starting of each point. For example:"1. This is the first point.\n2. This is another bullet point.\n\n3. And this is another with space between above line and so on."Do not include any instructions about subtitles, slide images, or point-by-point lists. The content provided should be detailed and ready for slide creation without additional formatting or instructions. Focus solely on the lesson content."""
#exp_prompt = """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""

slide_prompt = "give information in as short as possible"
exp_prompt = "Explain in as short as possible"


async def create_video_segments(title: str, speaker: str) -> List[str]:
    try:
        llm_response = get_llm_response(title, slide_prompt)
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        
        videos = []
        while extra_text:
            #exp_prompt = """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""
            voice_text = get_llm_response(written_text, exp_prompt)
            try:
                voice = await get_edge_tts(voice_text, speaker)
            except Exception as e:
                print(f"Error generating TTS: {e}")
                continue
            if voice:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)

       # exp_prompt = """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""
        voice_text = get_llm_response(written_text, exp_prompt)
        try:
            voice = await get_edge_tts(voice_text, speaker)
        except Exception as e:
            print(f"Error generating TTS: {e}")
            return videos
        if voice:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid:
                videos.append(final_vid)
        
        return videos
    except Exception as e:
        print(f"Error in create_video_segments: {e}")
        print(traceback.format_exc())
        return []

@app.post("/generate")
async def generate(title: str = Form(...), speaker: str = Form(...)):
    try:
        videos = await create_video_segments(title, speaker)
        if not videos:
            return JSONResponse(content={"error": "Failed to create video segments."}, status_code=500)
        
        final_video_path = "/assets/output/finalvideo.mp4"
        merge_videos(videos, final_video_path)
        return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path}, status_code=200)
    except Exception as e:
        error_message = f"Error in generate endpoint: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
