import os
import traceback
from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from plugins.slide import generate_background_image, write_text_on_image
from plugins.tiktok_tts import get_tt_tts
from plugins.merge_vid import merge_videos
from plugins.imgtovid import merge_image_and_audio
from plugins.elevenlabs_tts import get_elevenlabs_tts
from plugins.msedge_tts import get_edge_tts
from plugins.model import get_llm_response

app = FastAPI()

# Mount the static directory to serve the HTML file and other static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

async def fetch_tts(ask_tts, text, speaker):
    try:
        if ask_tts == 1:
            return await get_elevenlabs_tts(text, speaker)
        elif ask_tts == 2:
            return await get_edge_tts(text)
        elif ask_tts == 3:
            return await get_tt_tts(text)
    except Exception as e:
        raise Exception(f"Failed to fetch TTS voice: {e}")

@app.post("/generate")
async def generate(
    title: str = Form(...),
    ask_tts: int = Form(...),
    speaker: Optional[str] = Form(None)
):
    try:
        llm_response = get_llm_response(title, "You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.")
    except Exception as e:
        error_message = f"Failed to fetch LLM response: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    try:
        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        if background_image is None:
            raise ValueError("Failed to generate background image.")
    except Exception as e:
        error_message = f"Error generating background image: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    try:
        slide, extra_text, written_text = write_text_on_image(background_image, llm_response)
        if slide is None or written_text is None:
            raise ValueError("Failed to generate slide or written text.")
    except Exception as e:
        error_message = f"Error writing text on image: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    videos = []

    while extra_text:
        try:
            voice = await fetch_tts(ask_tts, written_text, speaker)
        except Exception as e:
            error_message = f"Error generating TTS: {e}"
            print(error_message)
            print(traceback.format_exc())
            return JSONResponse(content={"error": error_message}, status_code=500)

        if voice:
            try:
                vid = merge_image_and_audio(slide, voice)
                if vid is None:
                    raise ValueError("Failed to merge image and audio.")
                videos.append(vid)
            except Exception as e:
                error_message = f"Error merging image and audio: {e}"
                print(error_message)
                print(traceback.format_exc())
                return JSONResponse(content={"error": error_message}, status_code=500)

        try:
            background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
            if background_image is None:
                raise ValueError("Failed to generate background image.")
            slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
            if slide is None or written_text is None:
                raise ValueError("Failed to generate slide or written text.")
        except Exception as e:
            error_message = f"Error writing text on image: {e}"
            print(error_message)
            print(traceback.format_exc())
            return JSONResponse(content={"error": error_message}, status_code=500)

        if not extra_text:
            break

    try:
        voice = await fetch_tts(ask_tts, written_text, speaker)
    except Exception as e:
        error_message = f"Error generating TTS: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    if voice:
        try:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid is None:
                raise ValueError("Failed to merge final video.")
            videos.append(final_vid)
        except Exception as e:
            error_message = f"Error merging final video: {e}"
            print(error_message)
            print(traceback.format_exc())
            return JSONResponse(content={"error": error_message}, status_code=500)
    else:
        error_message = "Voice missing for final video."
        print(error_message)
        return JSONResponse(content={"error": error_message}, status_code=500)

    output_path = "static/finalvideo.mp4"
    try:
        merge_videos(videos, output_path)
    except Exception as e:
        error_message = f"Failed to merge videos: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    return JSONResponse(content={"url": f"/static/finalvideo.mp4"}, status_code=200)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
