"""Quick script to test Gemini API connectivity and find the right model."""
import google.generativeai as genai
import sys

API_KEY = "AIzaSyCPNd9PADIoEvuvt4rq6BJNIkTBTd0QAkc"

print(f"SDK version: {genai.__version__}")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
print()

# Configure
genai.configure(api_key=API_KEY)

# List available models
print("=== Available Models ===")
try:
    for model in genai.list_models():
        if "generate" in str(model.supported_generation_methods):
            print(f"  {model.name}")
except Exception as e:
    print(f"  Error listing models: {e}")

print()

# Try different model names
models_to_try = [
    "gemini-2.0-flash",
    "gemini-1.5-flash", 
    "gemini-pro",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-latest",
]

for model_name in models_to_try:
    try:
        print(f"Trying: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello in one word")
        print(f"SUCCESS -> {response.text.strip()}")
        break
    except Exception as e:
        print(f"FAILED -> {e}")
