import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


def get_gemini_response(SystemMessage, HumanMessage, image=None):
    if not image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
      
        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        result = llm.invoke(
                     [
                         SystemMessage(content=SystemMessage),
                         HumanMessage(content=HumanMessage),
                     ]
                 )
        return result.content
    img = None
    if image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
        with Image.open(image) as im:
            img = im
        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        result = llm.invoke(
                     [
                         SystemMessage(content=SystemMessage),
                         HumanMessage(content=[{"type": "text", "text": "What's in this image?"}, {"type": "image", "image": img}]),
                     ]
                 )
        return result.content
