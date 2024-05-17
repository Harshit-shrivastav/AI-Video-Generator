import requests
import os
import google.generativeai as genai
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = "AIzaSyAGe0LzEjcyRNZCtTMALDlsSRKsHLf_e84"

genai.configure(api_key=GOOGLE_API_KEY)

def get_groq_response(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_llm_response(Prompt, image=None):
    prompt = f"""You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.
    Topic :- {Prompt}
    Your Answer :- 
    """
    if image and GOOGLE_API_KEY:
        if prompt:
            img = Image.open(image)
            llm = genai.GenerativeModel('gemini-pro-vision')
            if img:
                response = llm.generate_content([prompt, img])
                return response.text
            else:
                return False 
    elif not image and GOOGLE_API_KEY:
        if prompt:
            llm = genai.GenerativeModel('gemini-pro')
            response = llm.generate_content(prompt)
            return response.text
    elif not GOOGLE_API_KEY:
        print("GOOGLE_API_KEY is missing")
        return False
    else:
        print("Unconditional Exception")
        return False
