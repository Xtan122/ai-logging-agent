from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Liệt kê tất cả các model khả dụng
models = client.models.list()
for model in models:
    print(f"Name: {model.name} | Display Name: {model.display_name}")