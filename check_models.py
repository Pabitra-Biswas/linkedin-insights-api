import google.generativeai as genai

# 1. Paste your NEW API Key here
API_KEY = "AIzaSyDuzGFsgHxBYx-4BuenZSrw29CGHcvtc50" # <--- PASTE YOUR KEY HERE

def list_available_models():
    try:
        genai.configure(api_key=API_KEY)
        
        print(f"\n🔍 Checking available models for key ending in ...{API_KEY[-4:]}\n")
        
        found = False
        for m in genai.list_models():
            # We only care about text generation models
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ FOUND: {m.name}")
                found = True
        
        if not found:
            print("❌ No text generation models found. Check your API Key permissions.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_available_models()