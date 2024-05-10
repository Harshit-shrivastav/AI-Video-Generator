import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


def get_gemini_response(SystemMessage, HumanMessage, image=None):
    if not image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
      
        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        result = model.invoke(
                     [
                         SystemMessage(content=SystemMessage),
                         HumanMessage(content=HumanMessage),
                     ]
                 )
        return result.content
    if image:
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
      
        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        result = model.invoke(
                     [
                         SystemMessage(content=SystemMessage),
                         HumanMessage(content=[ {"type": "text", "text": "What's in this image?",}, {"type": "image", "image": image}]),
                     ]
                 )
        return result.content



