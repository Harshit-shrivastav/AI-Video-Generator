import requests
import os
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyAGe0LzEjcyRNZCtTMALDlsSRKsHLf_e84"

genai.configure(api_key=GOOGLE_API_KEY)


def get_llm_response(Prompt, image=None):
    prompt = f'''{Prompt}'''
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
