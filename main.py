import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# မင်းပေးထားတဲ့ Token နဲ့ API Key ကို သေချာထည့်ထားတယ်
BOT_TOKEN = "8566707591:AAH-sEc5zGNUPRDbsiyefot4md7HtLJ0Mj8"
GEMINI_API_KEY = "AIzaSyCRAYgEzku8MpHru0TjhDmu7pVrk2itnL4"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot စဖွင့်တဲ့အချိန်ပြမယ့်စာသား"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 ဟိုင်း {user_name} သားကြီး!\n\n"
        "ငါက Node.js code တွေကို Python အဖြစ် Gemini AI သုံးပြီး ပြောင်းပေးမယ့် Bot ပါ။\n"
        "ပြောင်းချင်တဲ့ Node.js ကုဒ်တွေကို ဒီအတိုင်း Copy ကူးပြီး ပို့ပေးလိုက်ပါ။"
    )

async def convert_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Node.js ကို Python ပြောင်းပေးတဲ့ အဓိကအပိုင်း"""
    user_code = update.message.text
    
    # User ကို ခဏစောင့်ဖို့ ပြောမယ်
    status_msg = await update.message.reply_text("⏳ Gemini AI က Python ပြောင်းပေးနေတယ်... ခဏစောင့်နော်...")

    # Gemini API သို့ ပို့မယ့် URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # AI ကို ခိုင်းမယ့်စာ (Prompt)
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Please convert this Node.js code to clean and working Python code. Give only the code output, no extra text or explanations:\n\n{user_code}"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        # AI ဆီက ပြန်လာတဲ့ စာသားကို ယူမယ်
        python_code = data['candidates'][0]['content']['parts'][0]['text']

        # စာသားအရမ်းရှည်ရင် (၄၀၀၀ ထက်ကျော်ရင်) ဖိုင်အနေနဲ့ ပို့ပေးမယ်
        if len(python_code) > 4000:
            file_path = "converted_code.py"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(python_code)
            
            await update.message.reply_document(
                document=open(file_path, "rb"),
                filename="converted_code.py",
                caption="✅ ကုဒ်တွေ အရမ်းရှည်လို့ ဖိုင်အနေနဲ့ ပို့ပေးလိုက်တယ် သားကြီး!"
            )
        else:
            # Markdown နဲ့ ပို့ရင် ကုဒ်တွေက ကူးရတာ လွယ်တယ်
            await update.message.reply_text(
                f"✅ Python Code ရပါပြီ သားကြီး:\n\n```python\n{python_code}\n```",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error တက်သွားတယ်: {str(e)}")
    finally:
        # "စောင့်ပါ" ဆိုတဲ့ စာသားကို ပြန်ဖျက်မယ်
        await status_msg.delete()

def main():
    """Bot ကို စတင်အသက်သွင်းခြင်း"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Command တွေနဲ့ စာသားတွေကို လက်ခံဖို့ Handler တွေ ထည့်မယ်
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert_code))

    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
      
