import os
import requests
import xml.etree.ElementTree as ET
from html import unescape
import re
import time

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL_ID"]

RSS_URL = "https://reliefweb.int/jobs/rss.xml?advanced-search=%28C87%29"

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


# Get the RSS feed
response = requests.get(RSS_URL, timeout=30)
response.raise_for_status()

# Read RSS/XML
root = ET.fromstring(response.content)

# Get the 10 latest jobs
items = root.findall(".//item")[:10]

if not items:
    print("No jobs found in the RSS feed.")
    exit()

print(f"Found {len(items)} jobs.")


for number, item in enumerate(items, start=1):

    title = item.findtext("title", "No title")
    link = item.findtext("link", "")
    description = item.findtext("description", "")

    # Remove HTML from description
    description = unescape(description)
    description = re.sub(r"<[^>]+>", "", description)

    # Clean extra whitespace
    description = re.sub(r"\s+", " ", description).strip()

    # Limit description length
    description = description[:1000]

    # Create Telegram message
    message = f"""🔔 <b>NEW JOB OPPORTUNITY</b>

💼 <b>{title}</b>

{description}

🔗 <a href="{link}">View Job / Apply</a>

#HumanitarianJobs #Jobs
"""

    # Send to Telegram
    telegram_response = requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": CHANNEL,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        },
        timeout=30
    )

    print(f"Job {number}: Telegram status {telegram_response.status_code}")
    telegram_response.raise_for_status()

    print(f"✅ Posted: {title}")

    # Small delay between messages
    time.sleep(2)

print("🎉 All 10 jobs posted successfully!")
