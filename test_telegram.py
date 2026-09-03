import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL_ID"]

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

message = """🤖 <b>Ethiopia Jobs Finder</b>

The bot is now connected successfully!

RSS job monitoring will be added next.

#EthiopiaJobs #HumanitarianJobs
"""

response = requests.post(
    url,
    json={
        "chat_id": CHANNEL,
        "text": message,
        "parse_mode": "HTML"
    },
    timeout=30
)

print(response.status_code)
print(response.text)

response.raise_for_status()
