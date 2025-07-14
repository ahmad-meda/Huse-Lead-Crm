from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

# 
#  Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)