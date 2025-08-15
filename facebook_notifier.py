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
        self.USER_TOKEN = config.fb_user_token  # Long-lived user token
        self.PAGE_ID = config.fb_page_id

        self.TOKEN_FILE = "fb_user_token.json"

    def load_user_token(self):
        """
        Loads user token from local file if available, else from env.
        """
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, "r") as f:
                data = json.load(f)
            return data["access_token"], datetime.fromisoformat(data["expires_at"])
        else:
            # Use token from env with an assumed expiration ~60 days from now
            return self.USER_TOKEN, datetime.utcnow() + timedelta(days=59)

    def save_user_token(self, token, expires_in):
        """
        Saves the refreshed token and its expiry date to local file.
        """
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        with open(self.TOKEN_FILE, "w") as f:
            json.dump({
                "access_token": token,
                "expires_at": expires_at.isoformat()
            }, f)

    def refresh_user_token(self, user_token):
        """
        Refresh long-lived user token before it expires.
        """
        url = "https://graph.facebook.com/v23.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.APP_ID,
            "client_secret": self.APP_SECRET,
            "fb_exchange_token": user_token
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        print("User token refreshed.")
        self.save_user_token(data["access_token"], data["expires_in"])
        return data["access_token"]

    def get_page_access_token(self, user_token, page_id):
        """
        Fetch long-lived Page access token from user token.
        """
        url = "https://graph.facebook.com/v23.0/me/accounts"
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
        # Load user token
        user_token, expires_at = self.load_user_token()

        # Refresh if expiring in <10 days
        if (expires_at - datetime.utcnow()).days < 10:
            print("Token close to expiry, refreshing...")
            user_token = self.refresh_user_token(user_token)
        else:
            print(f" Token valid until {expires_at.isoformat()}")

        page_token = self.get_page_access_token(user_token, self.PAGE_ID)

        for post in posts:
            message = (
                f"{post['source_title']}\n"
                f"{post['summary']}"
                f"Odkaz na dokument: {post['url']}\n"
            )
            self.post_to_page(page_token, self.PAGE_ID, message)
