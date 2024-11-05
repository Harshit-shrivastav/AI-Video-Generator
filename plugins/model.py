import requests
import os
from PIL import Image 
import google.generativeai as genai
from groq import Groq
from config import GROQ_API_KEY, GOOGLE_API_KEY, CF_ACCOUNT_ID, CF_API_KEY 

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_cfai_response(account_id=CF_ACCOUNT_ID, auth_token=CF_API_KEY, model_name="@cf/meta/llama-3.1-8b-instruct", system_prompt, user_prompt):
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_name}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]}
    )
    return response.json().get('result', {}).get('response')

def get_groq_response(user_prompt, system_prompt):
    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def get_llm_response(user_prompt, system_prompt, image=None):
    formatted_prompt = f"""
    {system_prompt}
    Topic: {user_prompt}
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
            print(f"Error generating response with Google AI: {e}, trying with Groq if possible.")
            if GROQ_API_KEY:
                result = get_groq_response(user_prompt, system_prompt)
                return result
            else:
                print("No Groq API key found.")
                return False

    elif not GOOGLE_API_KEY and GROQ_API_KEY:
        if GROQ_API_KEY:
            result = get_groq_response(prompt)
            return result
        else:
            return False 
    elif not GOOGLE_API_KEY and not GROQ_API_KEY and CF_ACCOUNT_ID and CF_API_KEY:
        if CF_ACCOUNT_ID and CF_API_KEY:
            result = get_cfai_response(prompt)
            return result
        else:
            return False 
    else:
        print("No AI API Key Found!")
