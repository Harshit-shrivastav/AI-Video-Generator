import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

SYSTEM_MESSAGE = ''
HUMAN_MESSAGE = ''


import os
import getpass
from chat_google_generative_ai import ChatGoogleGenerativeAI

def get_gemini_response(system_message, human_message):
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Gemini API KEY is missing in environment.")
      
    llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
    result = llm.invoke(
                 [
                     system_message,
                     human_message,
                 ]
             )
    return result.content
