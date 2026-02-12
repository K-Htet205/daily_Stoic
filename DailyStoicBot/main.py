import os
# ... တခြား import များ ...

# API Keys တွေကို GitHub Secrets ကနေ လှမ်းဖတ်မယ်
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PDF_FILENAME = "daily_stoic.pdf"
from groq import Groq
import pdfplumber
import requests
import datetime

# --- ဖြည့်ရမယ့်နေရာများ ---
GROQ_API_KEY = "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"       # <--- Groq Key ပြန်ထည့်ပါ
TELEGRAM_BOT_TOKEN = "8576033231:AAGD9CeNKQIsveJul_hdX7orLExKdzS8NGc"    # Token ပြန်ထည့်ပါ
TELEGRAM_CHAT_ID = "7629887652"        # Chat ID ပြန်ထည့်ပါ
PDF_FILENAME = "daily_stoic.pdf"

# Groq Setup
client = Groq(api_key=GROQ_API_KEY)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

today = datetime.datetime.now().strftime("%B %d")
print(f"Checking for: {today}...")

try:
    with pdfplumber.open(PDF_FILENAME) as pdf:
        found_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text and today in text:
                found_text = text
                break 
        
        if found_text:
            print("စာတွေ့ပြီ! Groq (Llama 3.3) နဲ့ ဘာသာပြန်နေပါပြီ...")
            
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful translator. Translate the given text into natural, spoken Burmese. Start with a bold title. Explain the philosophy simply."
                        },
                        {
                            "role": "user",
                            "content": f"Here is the Daily Stoic passage:\n\n{found_text}"
                        }
                    ],
                    # --- ဒီနေရာ ပြောင်းထားပါတယ် (Model အသစ်) ---
                    model="llama-3.3-70b-versatile", 
                )

                result_text = chat_completion.choices[0].message.content

                if result_text:
                    send_telegram(f"📅 *Daily Stoic ({today})*\n\n{result_text}")
                    print("Telegram ပို့ပြီးပါပြီ! ✅ (Success!)")
                else:
                    print("Error: Groq က ဘာမှပြန်မဖြေပါ")

            except Exception as e:
                print(f"Groq API Error: {e}")
            
        else:
            print(f"PDF ထဲမှာ ဒီနေ့ ({today}) အတွက် စာမျက်နှာ ရှာမတွေ့ပါဘူး။")

except Exception as e:
    print(f"System Error: {e}")
    
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": """
            You are NOT a translator. You are a cool, wise older brother explaining Stoic philosophy to your younger brother in Myanmar.

            STRICT LANGUAGE RULES:
            1. Use ONLY Spoken Burmese (စကားပြောဟန်). 
            2. sentence endings must be 'တယ်', 'မယ်', 'နော်', 'ဗျ', 'ပါ'.
            3. FORBIDDEN WORDS: Never use 'သည်', '၏', 'သော', '၌', 'ဖြစ်သည်', 'ပါသည်', 'ဖော်ပြထားပါသည်'. These make you sound like a robot.
            4. Use simple, modern words that people actually use in daily life.

            STRUCTURE (Follow the user's favorite style):
            - 🌟 **[Title in catchy Burmese]**
            - ဒီနေ့အတွက် Stoic စာစုလေးကို အချက် (၃) ချက်နဲ့ အလွယ်ဆုံး ရှင်းပြပေးမယ်နော်။
            - ၁။ [Point 1: Human-like explanation]
            - ၂။ [Point 2: Human-like explanation]
            - ၃။ [Point 3: Human-like explanation]
            - **အတိုချုပ်ပြောရရင် -** [Warm, mentor-like summary ending with 'ဗျ']
            """
        },
        {
            "role": "user",
            "content": f"Explain this passage to me like a brother, no formal words: \n\n{found_text}"
        }
    ],
    model="llama-3.3-70b-versatile",
)