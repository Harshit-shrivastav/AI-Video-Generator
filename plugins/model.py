import requests
import os
from PIL import Image  # Assuming you need to handle image inputs
import google.generativeai as genai
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_groq_response(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_llm_response(prompt, image=None):
    formatted_prompt = f"""
    You are a teacher preparing slides for your students. Always explain concepts clearly and in a way that is easy to understand, as if you are presenting directly to them. Do not include any instructions about subtitles, slide images, or point-by-point lists. Ensure that your explanations are detailed and can be used directly to create slides without additional formatting or instructions. Focus solely on providing the content of the lesson.
    Topic: {prompt}
    Your Answer: 
    """

    if image and GOOGLE_API_KEY:
        try:
            img = Image.open(image)
            llm = genai.GenerativeModel('gemini-pro-vision')
            response = llm.generate_content([formatted_prompt, img])
            return response.text
        except Exception as e:
            print(f"Error generating response with image: {e}")
            return False

    elif not image and GOOGLE_API_KEY:
        try:
            llm = genai.GenerativeModel('gemini-pro')
            response = llm.generate_content(formatted_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response with Google AI: {e}, trying with grog if possible.")
            if GROQ_API_KEY:
                result = get_groq_response(prompt)
                return result
            else:
                print("No Groq API key found.")
                return False

    elif not GOOGLE_API_KEY:
        if GROQ_API_KEY:
            result = get_groq_response(prompt)
            return result
        else:
            print("No AI API key found.")
            return False
    else:
        print("Unconditional Exception")
        return False
