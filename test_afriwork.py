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
    deadline
    compensation_amount_cents
    compensation_type
    compensation_currency
    experience_level

    city {
      name
      country {
        name
      }
    }

    sectors {
      sector {
        name
      }
    }

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

response = requests.post(
    API_URL,
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

print(data)

jobs = data["data"]["jobs"]

print(f"\nFound {len(jobs)} jobs.\n")

for number, job in enumerate(jobs, start=1):

    print("=" * 60)
    print(f"JOB {number}")
    print("=" * 60)

    print("Title:", job["title"])
    print("Company:", job["entity"]["name"] if job.get("entity") else "N/A")
    print("Job type:", job.get("job_type"))
    print("Job site:", job.get("job_site"))
    print("Experience:", job.get("experience_level"))
    print("Deadline:", job.get("deadline"))

    if job.get("city"):
        print("Location:", job["city"]["name"])

        if job["city"].get("country"):
            print("Country:", job["city"]["country"]["name"])

    print("Published:", job.get("published_at"))
    print("ID:", job["id"])
