from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import os

# Import your helper functions from your_module
from plugins import (
    generate_background_image, write_text_on_image, get_tt_tts,
    merge_videos, merge_image_and_audio, get_elevenlabs_tts, get_edge_tts, get_llm_response
)

app = FastAPI()

# Mount the static directory to serve the HTML file and other static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate")
async def generate(
    title: str = Form(...),
    ask_tts: int = Form(...),
    speaker: Optional[str] = Form(None)
):
    try:
        llm_response = get_llm_response(title, "You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.")
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to fetch LLM response: {e}"}, status_code=500)

    background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
    if not background_image:
        return JSONResponse(content={"error": "Failed to generate background image."}, status_code=500)

    slide, extra_text, written_text = write_text_on_image(background_image, llm_response)

    if not slide or not written_text:
        return JSONResponse(content={"error": "Failed to generate slide or written text."}, status_code=500)

    videos = []

    while extra_text:
        voice = None
        try:
            if ask_tts == 1:
                voice = get_elevenlabs_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."), speaker)
            elif ask_tts == 2:
                voice = get_edge_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."))
            elif ask_tts == 3:
                voice = get_tt_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."))
        except Exception as e:
            return JSONResponse(content={"error": f"Failed to fetch TTS voice: {e}"}, status_code=500)

        if voice:
            try:
                vid = merge_image_and_audio(slide, voice)
                if vid:
                    videos.append(vid)
            except Exception as e:
                return JSONResponse(content={"error": f"Error merging image and audio: {e}"}, status_code=500)

        background_image = generate_background_image(1600, 900, (255, 255, 255), 50, (135, 206, 235))
        slide, extra_text, written_text = write_text_on_image(background_image, extra_text)
        if not extra_text:
            break

    voice = None
    try:
        if ask_tts == 1:
            voice = get_elevenlabs_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."), speaker)
        elif ask_tts == 2:
            voice = get_edge_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."))
        elif ask_tts == 3:
            voice = get_tt_tts(get_llm_response(written_text, "You are a very talented and creative teacher. Your ability to explain chapters or paragraphs is exceptional, making complex ideas simple and engaging. Please explain the given content clearly and creatively, ensuring that anyone, including children, can understand. Do not include any extra comments, such as 'Sure, I can explain,' or any other unrelated remarks. Focus solely on the topic at hand, providing a thorough and comprehensible explanation."))
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to fetch TTS voice: {e}"}, status_code=500)

    if voice:
        try:
            final_vid = merge_image_and_audio(slide, voice)
            if final_vid:
                videos.append(final_vid)
            else:
                return JSONResponse(content={"error": "Failed to merge final video."}, status_code=500)
        except Exception as e:
            return JSONResponse(content={"error": f"Error merging final video: {e}"}, status_code=500)
    else:
        return JSONResponse(content={"error": "Voice missing for final video."}, status_code=500)

    output_path = "static/finalvideo.mp4"
    try:
        merge_videos(videos, output_path)
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to merge videos: {e}"}, status_code=500)

    return JSONResponse(content={"url": f"/static/finalvideo.mp4"}, status_code=200)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
