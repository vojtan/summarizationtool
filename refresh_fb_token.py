import requests
import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

# Facebook token refresh
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_USER_TOKEN = os.getenv("FB_USER_TOKEN")  # Current token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")    # GitHub personal access token with repo access
GITHUB_REPO = "vojtan/summarizationtool"               # Format: owner/repo
SECRET_NAME = "FB_USER_TOKEN"               # Name of the secret in GitHub

def refresh_fb_token(app_id, app_secret, user_token):
    url = "https://graph.facebook.com/v23.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_token
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]

def update_github_secret(repo, secret_name, secret_value, github_token):
    # Get public key for encrypting the secret
    headers = {"Authorization": f"token {github_token}"}
    url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    key_data = resp.json()
    public_key = key_data["key"]
    key_id = key_data["key_id"]

    # Encrypt the secret value using the public key
    from base64 import b64encode
    from nacl import encoding, public

    def encrypt(public_key: str, secret_value: str) -> str:
        public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return b64encode(encrypted).decode("utf-8")

    encrypted_value = encrypt(public_key, secret_value)

    # Update the secret
    url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    resp = requests.put(url, headers=headers, json=payload)
    resp.raise_for_status()
    print(f"Secret {secret_name} updated successfully.")

if __name__ == "__main__":
    new_token = refresh_fb_token(FB_APP_ID, FB_APP_SECRET, FB_USER_TOKEN)
    update_github_secret(GITHUB_REPO, SECRET_NAME, new_token, GITHUB_TOKEN)