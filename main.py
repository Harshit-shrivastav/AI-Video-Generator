import traceback
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import List

from plugins.slide import generate_background_image, write_text_on_image
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.elevenlabs_tts import get_elevenlabs_tts
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

def create_video_segments(title: str, speaker: str) -> List[str]:
    try:
        llm_response = get_llm_response(title, "Provide educational content...")
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        
        videos = []
        while extra_text:
            voice = await fetch_tts(get_llm_response(written_text, "Provide detailed explanation..."), speaker)
            if voice:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)

        voice = await fetch_tts(get_llm_response(written_text, "Provide detailed explanation..."), speaker)
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
        videos = create_video_segments(title, speaker)
        if not videos:
            return JSONResponse(content={"error": "Failed to create video segments."}, status_code=500)
        
        final_video_path = "assets/output/finalvideo.mp4"
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
