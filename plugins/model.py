import requests
import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAGe0LzEjcyRNZCtTMALDlsSRKsHLf_e84")


def get_llm_response(Prompt, image=None):
    prompt = f'''{Prompt}'''
    if image and "GOOGLE_API_KEY" in os.environ:
        if prompt:
            img = Image.open(image)
            llm = genai.GenerativeModel('gemini-pro-vision')
            if img:
                response = llm.generate_content([prompt, img])
                print(response.text)
                return response.text
            else:
                return False
    elif (image and "GOOGLE_API_KEY" not in os.environ):
        print("Please set GOOGLE_API_KEY as environment variable, to use image.")
        return False
    elif (not image and "GOOGLE_API_KEY" not in os.environ):
        print("GOOGLE_API_KEY is missing")
        return False 
    elif (not image and "GOOGLE_API_KEY" in os.environ):
        if prompt:
            llm = genai.GenerativeModel('gemini-pro')
            response = llm.generate_content(prompt)
            print(response.text)
            return response.text
    else:
        return False 
