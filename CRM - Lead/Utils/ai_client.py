from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

# 
# #  Initialize OpenAI client
# client = OpenAI(
#     api_key=os.getenv("GEMINI_API_KEY"),
#     base_url="https://generativelanguage.googleapis.com/v1/"
#     # base_url = "http://localhost:3001/proxy/gemini"
# )

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# from google import genai
# import dotenv
# import os

# dotenv.load_dotenv()

# # 
# #  Initialize OpenAI client
# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY"),
# )