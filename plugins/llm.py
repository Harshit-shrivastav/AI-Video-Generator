import requests
import os
import google.generativeai as genai
from PIL import Image 

def chatgpt(msg):
    url = f'https://api.voidevs.com/gpt/free?msg={msg}'
    try:
        respons = requests.get(url)
        if respons.status_code == 200:
            response_text = respons.text
            response_dict = json.loads(response_text)
            if response_dict['result']:
                return response_dict['results']['answer']
            else:
                return False
        else:
            return False
    except:
        return False


def get_llm_response(prompt, image=None):
    if image and "GOOGLE_API_KEY" in os.environ:
        if prompt:
            img = PIL.Image.open(image)
            llm = genai.GenerativeModel('gemini-pro')
            if img:
                response = model.generate_content(prompt, img)
                return response.text
            else:
                return False
    elif (image and "GOOGLE_API_KEY" not in os.environ):
        print("Please set GOOGLE_API_KEY as environment variable, to use image.")
        return False
    elif (not image and "GOOGLE_API_KEY" not in os.environ):
        if prompt:
            result = chatgpt(prompt)
            if result:
                return result
            else:
                return False 
    elif (not image and "GOOGLE_API_KEY" in os.environ):
        if prompt:
            llm = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
    else:
        return False 
        
                  




