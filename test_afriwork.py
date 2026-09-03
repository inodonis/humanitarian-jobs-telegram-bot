import os
import requests
import re
from html import unescape
import time

API_URL = "https://api.afriworket.com/v1/graphql"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL_ID"]

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


query = """
query GetAllJobs($offset: Int!, $whereCondition: jobs_bool_exp!, $orderCondition: [jobs_order_by!]) {
  jobs(
    order_by: $orderCondition
    offset: $offset
    limit: 10
    where: $whereCondition
  ) {
    id
    title
    created_at
    published_at
    refreshed_at
    description
    job_type
    job_site

    city {
      name
      country {
        name
      }
    }

    deadline
    compensation_amount_cents
    compensation_type
    compensation_currency
    experience_level

    entity {
      type
      name
    }
  }
}
"""


variables = {
    "offset": 0,
    "orderCondition": {
        "latest_activity_at": "desc"
    },
    "whereCondition": {
        "_and": [
            {
                "approval_status": {
                    "_in": ["PUBLISHED", "REFRESHED"]
                }
            }
        ]
    }
}


headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://afriworket.com",
    "Referer": "https://afriworket.com/",
    "x-hasura-role": "anonymous"
}


# Get jobs from Afriwork
response = requests.post(
    API_URL,
    headers=headers,
    json={
        "operationName": "GetAllJobs",
        "query": query,
        "variables": variables
    },
    timeout=30
)

response.raise_for_status()

data = response.json()

if "errors" in data:
    print("Afriwork API returned an error:")
    print(data["errors"])
    raise SystemExit(1)

jobs = data["data"]["jobs"]

print(f"Found {len(jobs)} Afriwork jobs.")


for number, job in enumerate(jobs, start=1):

    title = job.get("title") or "Untitled Job"

    # Company
    entity = job.get("entity")
    company = entity.get("name") if entity else "Not specified"

    # Location
    city = job.get("city")

    if city:
        location = city.get("name") or "Not specified"

        country = city.get("country")

        if country and country.get("name"):
            location = f"{location}, {country['name']}"
    else:
        location = "Not specified"

    # Description
    description = job.get("description") or ""

    description = unescape(description)

    # Remove HTML
    description = re.sub(r"<[^>]+>", "", description)

    # Clean whitespace
    description = re.sub(r"\s+", " ", description).strip()

    # Limit description
    description = description[:1500]

    # Other information
    job_type = job.get("job_type") or "Not specified"
    job_site = job.get("job_site") or "Not specified"
    experience = job.get("experience_level") or "Not specified"
    deadline = job.get("deadline") or "Not specified"

    # Afriwork job URL
    job_id = job.get("id")

    job_url = f"https://afriworket.com/jobs/{job_id}"


    # Create Telegram message
    message = f"""🔔 <b>NEW JOB — AFRIWORK</b>

💼 <b>{title}</b>

🏢 <b>Company:</b> {company}
📍 <b>Location:</b> {location}
💼 <b>Job type:</b> {job_type}
🏢 <b>Work site:</b> {job_site}
📊 <b>Experience:</b> {experience}

📅 <b>Deadline:</b> {deadline}

📝 <b>Description:</b>
{description}

🔗 <a href="{job_url}">View Job / Apply</a>

#Afriwork #EthiopiaJobs #Jobs
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

    print(
        f"Job {number}: Telegram status "
        f"{telegram_response.status_code}"
    )

    telegram_response.raise_for_status()

    print(f"✅ Posted: {title}")

    # Wait between messages
    time.sleep(2)


print("\n🎉 All Afriwork jobs posted successfully!")
