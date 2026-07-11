import os
from dotenv import load_dotenv
from google import genai 

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: Gemini API key not found in .env file.")
    exit(1)


client = genai.Client(api_key=api_key) 

# Test with a simple log analysis
sample_log = """
2024-10-21 14:23:45 ERROR Database connection failed
2024-10-21 14:23:46 WARN Retry attempt 1 of 3
2024-10-21 14:23:48 ERROR Database connection failed
2024-10-21 14:23:49 WARN Retry attempt 2 of 3
2024-10-21 14:23:51 ERROR Database connection failed
2024-10-21 14:23:52 ERROR Maximum retries reached
"""

# Ask the AI to analyze the log
prompt = f"""You are a senior DevOps engineer analyzing application logs.
Analyze this log and explain what's happening:
{sample_log}
Provide a brief analysis and suggest what might be wrong."""

print("Sending log analysis request to AI...")
print("-" * 50)

'''
response = client.models.generate_content(
    model="models/gemini-3.5-flash",
    contents=prompt
)
'''

interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input=prompt
)

#print(response.text)
print(interaction.output_text)

print("-" * 50)
print("Log analysis completed.")