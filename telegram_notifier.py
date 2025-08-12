from config import AppConfig
import requests

class TelegramNotifier:
    def __init__(self):
        config = AppConfig()
        self.telegram_token = config.telegram_token
        self.telegram_chat_id = config.telegram_chat_id

    def send_messages_to_telegram(self, all_new_pdfs):
        for pdf_info in all_new_pdfs:
            message = f"""
                <b>Název:</b> {pdf_info['source_title']}
                <b>PDF:</b> <a href=\"{pdf_info['url']}\">Stáhnout dokument</a>
                <b>Souhrn:</b>
                {pdf_info['summary']}
            """.strip()
            self.send_telegram_message(message)

    def send_telegram_message(self, message: str):
        """Send message to Telegram chat"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            print("Message sent to Telegram successfully")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")