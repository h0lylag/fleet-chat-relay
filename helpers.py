import datetime
import re
import requests
from config import Config


def send_to_discord(message, WEBHOOK_URL):
    payload = {
        "username": Config.DISCORD_WEBHOOK_NAME,      # use the name from your config
        "avatar_url": Config.DISCORD_WEBHOOK_AVATAR,    # use the avatar from your config
        "content": message
    }
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code not in (200, 204):
        print(f"Discord webhook error: {response.status_code} - {response.text}")


def extract_eve_timestamp(line):
    """
    Look for a fleet chat timestamp in the line.
    Expected format: [ YYYY.MM.DD HH:MM:SS ]
    Returns a unix timestamp (int) if found, else None.
    """
    match = re.search(r'\[\s*(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})\s*\]', line)
    if match:
        try:
            dt = datetime.datetime.strptime(match.group(1), '%Y.%m.%d %H:%M:%S')
            return int(dt.timestamp())
        except Exception as e:
            print("Timestamp parsing error:", e)
    return None


def unix_timestamp():
    return int(datetime.datetime.now().timestamp())
