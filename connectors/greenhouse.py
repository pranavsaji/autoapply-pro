import requests
from typing import List
from apps.api.models.domain import Job

API = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

class GreenhouseConnector:
    def search(self, company: str) -> List[Job]:
        url = API.format(company=company)
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        jobs = []
        for j in r.json().get("jobs", []):
            jobs.append(Job(
                id=str(j["id"]),
                title=j("title"),
                company=company,
                url=j("absolute_url"),
                location=(j.get("location") or {}).get("name"),
                source="greenhouse",
            ))
        return jobs