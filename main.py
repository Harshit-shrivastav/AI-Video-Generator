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
        llm_response = get_llm_response(title, """You are preparing educational slides for students. Ensure concepts are explained clearly and simply, as if presenting directly to the students. Use bullet points for all information. Do not write paragraphs except for subjects like math where step-by-step explanations are necessary. For theoretical subjects, always use bullet points. Separate each point with '\n' to break the line and '\n\n' to beak the lines two times, means insert the space between lines and use (1,2,3...) or by '*' for bullet signs add make sure to insert bullet signs in starting of each point. For example:"1. This is the first point.\n2. This is another bullet point.\n\n3. And this is another with space between above line and so on."Do not include any instructions about subtitles, slide images, or point-by-point lists. The content provided should be detailed and ready for slide creation without additional formatting or instructions. Focus solely on the lesson content.""")
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
            voice = await fetch_tts(get_llm_response(written_text, """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""), speaker)
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
        voice = await fetch_tts(get_llm_response(written_text, """You are a talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as "I can explain," or any other unrelated remarks. Focus solely on the lines at hand, providing a thorough and comprehensible explanation. Adjust the depth of your explanation according to the length of the text: less text requires a shorter explanation, more text requires a longer explanation."""), speaker)
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
    except Exception as e:
        error_message = f"Failed to merge videos: {e}"
        print(error_message)
        print(traceback.format_exc())
        return JSONResponse(content={"error": error_message}, status_code=500)

    return JSONResponse(content={"message": "Final video created successfully!", "video_path": final_video_path}, status_code=200)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
