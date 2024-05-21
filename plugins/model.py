import os
from llmware.prompts import Prompt
from groq import Groq

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', 'Grig_api_key')

def get_response(user_prompt) -> str:
    prompter = Prompt().load_model("phi-3-gguf")
    output = prompter.prompt_main(
        user_prompt, prompt_name="default_with_context", temperature=0.30
    )
    response = output["llm_response"].strip("\n").partition("")[0]
    return response

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

def get_llm_response(user_prompt, system_prompt):
    formatted_prompt = f"""
    {system_prompt}
    Topic: {user_prompt}
    Your Answer: 
    """
    try:
        response = get_response(formatted_prompt)
        return response
    except Exception as e:
        print(f"Error generating response with LLMWare AI: {e}, trying with Groq if possible.")
        if GROQ_API_KEY:
            result = get_groq_response(user_prompt, system_prompt)
            return result
        else:
            print("No Groq API key found.")
            return False
