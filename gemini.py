import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

def run(user_prompt):
    try:

        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt ,
        )
        return response.text
    except Exception as error:
        print("Error generating content from Gemini:", error)
        return False

