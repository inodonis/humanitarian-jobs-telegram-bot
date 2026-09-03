import requests

API_URL = "https://api.afriworket.com/v1/graphql"

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
    updated_at
    published_at
    refreshed_at
    approval_status
    description
    job_type
    job_site

    skill_requirements {
      skill {
        name
        id
      }
    }

    city {
      name
      country {
        name
      }
    }

    sectors {
      sector {
        name
        id
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

print("Status:", response.status_code)

response.raise_for_status()

data = response.json()

print("\nAPI response received.")

if "errors" in data:
    print("\nAPI returned an error:")
    print(data["errors"])
    raise SystemExit(1)

jobs = data["data"]["jobs"]

print(f"\nFound {len(jobs)} jobs.\n")

for number, job in enumerate(jobs, start=1):

    print("=" * 60)
    print(f"JOB {number}")
    print("=" * 60)

    print("Title:", job.get("title"))

    entity = job.get("entity")
    print("Company:", entity.get("name") if entity else "N/A")

    print("Job type:", job.get("job_type"))
    print("Job site:", job.get("job_site"))
    print("Experience:", job.get("experience_level"))
    print("Deadline:", job.get("deadline"))

    city = job.get("city")

    if city:
        print("Location:", city.get("name"))

        country = city.get("country")

        if country:
            print("Country:", country.get("name"))

    print("Published:", job.get("published_at"))
    print("ID:", job.get("id"))

print("\nSUCCESS: Afriwork API is working.")
