import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
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
        with Image.open(image) as img:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            message = HumanMessage(content=[{"type": "text", "text": prompt},{"type": "image_url", "image_url": img}])
            result = llm.invoke(message)
            return result.content
    elif (image and "GOOGLE_API_KEY" not in os.environ):
        print("Please set GOOGLE_API_KEY as environment variable, to use image.")
        return False
    elif (not image and "GOOGLE_API_KEY" not in os.environ):
        if prompt:
            result = chatgpt(prompt)
            if result:
                return result
    elif (not image and "GOOGLE_API_KEY" in os.environ):
        if prompt:
            result = chatgpt(prompt)
            if result:
                return result
    else:
        return False 
        
                  




