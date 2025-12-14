import time
import pickle
import os
from selenium import webdriver

# ================= CONFIGURATION =================
# 1. Update with your credentials
EMAIL = "your_email@example1.com"
PASSWORD = "your_password1"

# 2. Path to save (Save directly to your uploads folder to save time)
# Ensure this path exists!
SAVE_PATH = "data/uploads/linkedin_cookies.pkl" 
# =================================================

def get_cookies():
    print("🚀 Starting Local Browser to capture cookies...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # ⭐ IMPORTANT: This matches the User-Agent in your Docker scraper.py
    # If these don't match, LinkedIn invalidates the cookies immediately.
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Disable automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    
    try:
        print("🌐 Navigating to LinkedIn Login...")
        driver.get("https://www.linkedin.com/login")
        
        print("⚠️  PLEASE LOG IN MANUALLY NOW ⚠️")
        print("1. Enter Email & Password")
        print("2. Click Sign In")
        print("3. SOLVE THE PUZZLE / CAPTCHA if it appears")
        print("4. Wait until you see the LinkedIn News Feed")

        # Loop until we are logged in
        while True:
            try:
                current_url = driver.current_url
                if "feed" in current_url or "mynetwork" in current_url:
                    print("\n✅ Login Success! Feed detected.")
                    break
                if "checkpoint" in current_url:
                    print("🧩 Challenge detected - please solve it...", end="\r")
                time.sleep(1)
            except:
                pass

        # Wait a moment for cookies to settle
        time.sleep(5)

        # Ensure directory exists
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

        # Save Cookies
        cookies = driver.get_cookies()
        with open(SAVE_PATH, 'wb') as f:
            pickle.dump(cookies, f)
        
        print(f"\n💾 Cookies saved successfully to: {os.path.abspath(SAVE_PATH)}")
        print("✅ You can now restart your Docker container.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_cookies()