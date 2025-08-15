from logging import config
import os
import requests
import json
from datetime import datetime, timedelta

from config import AppConfig

class FacebookNotifier:
    def __init__(self):
        config = AppConfig()
        self.APP_ID = config.fb_app_id
        self.APP_SECRET = config.fb_app_secret
        self.USER_TOKEN = config.fb_user_token  
        self.PAGE_ID = config.fb_page_id



    def get_page_access_token(self, user_token, page_id):
        """
        Fetch long-lived Page access token from user token.
        """
        url = "https://graph.facebook.com/v23.0/me/accounts"
        try:
            resp = requests.get(url, params={"access_token": user_token})
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            print(f"Error fetching page access token: {e}")
            print(f"Response content: {getattr(resp, 'text', None)}")
            print(f"User token: {user_token}")
            raise
        resp = requests.get(url, params={"access_token": user_token})
        resp.raise_for_status()
        data = resp.json()
        for page in data.get("data", []):
            if page["id"] == page_id:
                return page["access_token"]
        raise ValueError("Page ID not found or token invalid")

    def post_to_page(self, page_token, page_id, message):
        """
        Post a message to the Facebook page.
        """
        url = f"https://graph.facebook.com/v23.0/{page_id}/feed"
        payload = {
            "message": message,
            "access_token": page_token
        }
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return resp.json()
    def create_posts(self, posts):
        """Send a notification message to the configured Facebook page.
        """
        page_token = self.get_page_access_token(self.USER_TOKEN, self.PAGE_ID)

        for post in posts:
            message = (
                f"{post['source_title']}\n"
                f"{post['summary']}"
                f"Odkaz na dokument: {post['url']}\n"
            )
            self.post_to_page(page_token, self.PAGE_ID, message)
