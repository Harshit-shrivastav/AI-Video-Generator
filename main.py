import os
import traceback
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from plugins.slide import generate_background_image, write_text_on_image
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.elevenlabs_tts import get_elevenlabs_tts
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

async def fetch_tts(text: str, speaker: str) -> bytes:
    try:
        tts_data = await get_edge_tts(text, speaker)
    except Exception as e:
        print(e)
        raise e
    return tts_data

@app.post("/generate")
async def generate(title: str = Form(...), speaker: str = Form(...)):
    try:
        llm_response = get_llm_response(title, """Your LLM response here""")
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
            voice = await fetch_tts(get_llm_response(written_text, """Your LLM response here"""), speaker)
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
        voice = await fetch_tts(get_llm_response(written_text, """Your LLM response here"""), speaker)
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

    final_video_path = "assets/output/finalvideo.mp4"
    try:
        merge_videos(videos, final_video_path)
        print("Final video created successfully!")
        return JSONResponse(content={"step": "video_ready", "video_path": final_video_path}, status_code=200)
    except Exception as e:
        error_message = f"Failed to merge videos: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
