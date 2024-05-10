import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from PIL import Image 

def get_gemini_response(prompt, image=None):
    if not image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        result = llm.invoke(prompt)
        return result.content
    if image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
        with Image.open(image) as img:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
            result = llm.invoke(prompt, img)
            return result.content
