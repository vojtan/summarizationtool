#!/usr/bin/env python3
"""
Děčín City Council PDF Monitor
Monitors city council URLs for new PDF documents and posts summaries to Telegram
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urljoin
import time
from bs4 import BeautifulSoup
import PyPDF2
import google.generativeai as genai
from config import AppConfig
from facebook_notifier import FacebookNotifier
from rss_feed_updater import RssFeedUpdater
from telegram_notifier import TelegramNotifier

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass


class DecinPDFMonitor:
    def __init__(self):
        self.config = AppConfig()

        # Configure Gemini
        genai.configure(api_key=self.config.gemini_api_key)
        self.model = genai.GenerativeModel(self.config.gemini_model_name)
        # File to track processed PDFs
        self.tracking_file = "processed_pdfs.json"

        # Load previously processed PDFs
        # self.processed_pdfs = self.load_processed_pdfs()

        # Create TelegramNotifier instance
        self.notifier = TelegramNotifier()
        self.rss_feed = RssFeedUpdater()
        self.facebook_notifier = FacebookNotifier()
       
    def download_pdf_content(self, pdf_url: str) -> str:
        """Download and extract text from PDF"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save PDF temporarily
            temp_pdf = f"temp_{hashlib.md5(pdf_url.encode()).hexdigest()}.pdf"
            with open(temp_pdf, 'wb') as f:
                f.write(response.content)
            
            # Extract text using PyPDF2
            text = ""
            try:
                with open(temp_pdf, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            finally:
                # Clean up temp file
                if Path(temp_pdf).exists():
                    Path(temp_pdf).unlink()
            
            return text.strip()
            
        except Exception as e:
            print(f"Error downloading/processing PDF {pdf_url}: {e}")
            return ""

    def generate_summary(self, text: str, title: str) -> str:
        """Generate summary using Google Gemini"""
        try:

            prompt = self.config.gemini_prompt.format(title=title, text=text)
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating summary with Gemini: {e}")
            # Fallback to simple summary
            lines = text.split('\n')
            summary_lines = [line.strip() for line in lines[:10] if line.strip()]
            return f"Automatický souhrn dokumentu '{title}':\n\n" + '\n'.join(summary_lines)


def main():
    """Main entry point"""
    # Validate environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your GitHub repository secrets.")
        return 1
    
    try:
        monitor = DecinPDFMonitor()
        content = monitor.download_pdf_content("https://www.mmdecin.cz/ostatni-dokumenty/zastupitelstvo-a-rada-mesta-decin/zapisy-z-jednani-komisi-rady-mesta/volebni-obdobi-2022-2026/komise-pro-urbanismus-a-architekturu-1/6960-2025-zapis-komise-pro-urbanismus-a-architekturu-20250825/file")
        test =  monitor.generate_summary(content, "")
        print(test)
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

