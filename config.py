import os
import json

class AppConfig:
    def __init__(self):
        self.fb_app_id = os.getenv('FB_APP_ID')
        self.fb_app_secret = os.getenv('FB_APP_SECRET')
        self.fb_user_token = os.getenv('FB_USER_TOKEN')
        self.fb_page_id = os.getenv('FB_PAGE_ID')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model_name = os.getenv('GEMINI_MODEL_NAME')
        self.gemini_prompt = os.getenv('GEMINI_PROMPT')
        urls_json = os.getenv('URLS_TO_MONITOR')
        self.urls_to_monitor = json.loads(urls_json) if urls_json else []
