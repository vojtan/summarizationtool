import os

class AppConfig:
    def __init__(self):
        self.fb_app_id = os.getenv('FB_APP_ID')
        self.fb_app_secret = os.getenv('FB_APP_SECRET')
        self.fb_user_token = os.getenv('FB_USER_TOKEN')
        self.fb_page_id = os.getenv('FB_PAGE_ID')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.urls_to_monitor = [
            {"title": "Usnesení rady města", "url": "https://www.mmdecin.cz/usneseni-rm/rok-2025"},
            {"title": "Usnesení zastupitelstva města", "url": "https://www.mmdecin.cz/usneseni-zm/2025-7"},
            {"title": "Kontrolní výbor", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-vyboru-zastupitelstva-mesta/kontrolni-vybor/2025-9"},
            {"title": "Finanční výbor", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-vyboru-zastupitelstva-mesta/financni-vybor/2025-8"},
            {"title": "Sociální komise", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/socialni-komise"},
            {"title": "Sportovní komise", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/sportovni-komise-1"},
            {"title": "Školská komise", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/skolska-komise-1"},
            {"title": "Kulturní komise", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/kulturni-komise-1"},
            {"title": "Komise pro urbanismus a architekturu", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/komise-pro-urbanismus-a-architekturu-1"},
            {"title": "Komise pro posuzování návrhů na cenu města", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/komise-pro-posuzovani-navrhu-na-udeleni-ceny-statutarniho-mesta-decin-1"},
            {"title": "Dopravní komise", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/dopravni-komise-1"},
            {"title": "Osadní výbor Dolní Žleb", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-vyboru-zastupitelstva-mesta/osadni-vybor-dolni-zleb/2025-11"},
            {"title": "Osadní výbor Křešice", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-vyboru-zastupitelstva-mesta/osadni-vybor-kresice/2025-12"},
            {"title": "Osadní výbor Maxičky", "url": "https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-vyboru-zastupitelstva-mesta/osadni-vybor-maxicky/2025-13"}
        ]
