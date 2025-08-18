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
        self.processed_pdfs = self.load_processed_pdfs()

        # Create TelegramNotifier instance
        self.notifier = TelegramNotifier()
        self.rss_feed = RssFeedUpdater()
        self.facebook_notifier = FacebookNotifier()
        
    def load_processed_pdfs(self) -> Set[str]:
        """Load list of previously processed PDF URLs"""
        try:
            if Path(self.tracking_file).exists():
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_pdfs', []))
        except Exception as e:
            print(f"Error loading tracking file: {e}")
        return set()
    
    def save_processed_pdfs(self):
        """Save list of processed PDF URLs"""
        try:
            data = {
                'processed_pdfs': list(self.processed_pdfs),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving tracking file: {e}")
    
    def get_pdf_links_from_page(self, url: str) -> List[Dict[str, str]]:
        """Extract PDF links from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = []
            
            # Find all links that end with .pdf
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('/file'):
                    # Convert relative URLs to absolute
                    full_url = urljoin(url, href)
                    title = link.get_text(strip=True) or link.get('title', '')
                    
                    pdf_links.append({
                        'url': full_url,
                        'title': title,
                        'source_page': url
                    })
            
            return pdf_links
            
        except Exception as e:
            print(f"Error fetching PDF links from {url}: {e}")
            return []
    
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

    
    def process_new_pdfs(self):
        """Main function to check for new PDFs and process them"""
        print(f"Starting PDF monitoring at {datetime.now()}")
        
        all_new_pdfs = []
        
        # Check each monitored URL
        for item in self.config.urls_to_monitor:
            print(f"Checking URL: {item['url']}")
            pdf_links = self.get_pdf_links_from_page(item['url'])
            
            # Filter out already processed PDFs
            new_pdfs = [pdf for pdf in pdf_links if pdf['url'] not in self.processed_pdfs]
            
            if new_pdfs:
                print(f"Found {len(new_pdfs)} new PDFs on {item['url']}")
                # Add the source title to each new PDF entry
                for pdf in new_pdfs:
                    pdf['source_title'] = item['title']
                all_new_pdfs.extend(new_pdfs)
            else:
                print(f"No new PDFs found on {item['url']}")
            
            # Small delay between requests
            time.sleep(2)
        
        if not all_new_pdfs:
            print("No new PDFs found across all monitored URLs")
            return
        
        # Process each new PDF
        for pdf_info in all_new_pdfs:
            try:
                print(f"Processing: {pdf_info['title']} - {pdf_info['url']}")
                pdf_text = self.download_pdf_content(pdf_info['url'])
                if not pdf_text:
                    print(f"Could not extract text from {pdf_info['url']}")
                    pdf_info['summary'] = "Byl přidán nový dokument, nepodařilo se ale získat text z dokumentu. "
                else:
                    pdf_info['summary'] = self.generate_summary(pdf_text, pdf_info['title'])
                self.processed_pdfs.add(pdf_info['url'])
                
                # Small delay between processing
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing PDF {pdf_info['url']}: {e}")
                continue
        

        self.notifier.send_messages_to_telegram(all_new_pdfs)
        self.rss_feed.update_feed(all_new_pdfs)
        self.facebook_notifier.create_posts(all_new_pdfs)
        self.save_processed_pdfs()
        print(f"Processed {len(all_new_pdfs)} new PDFs")


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
        monitor.process_new_pdfs()
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())