import requests
from typing import List
from apps.api.models.domain import Job

API = "https://api.lever.co/v0/postings/{company}?mode=json"

class LeverConnector:
    def search(self, company: str) -> List[Job]:
        url = API.format(company=company)
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        jobs = []
        for j in r.json():
            jobs.append(Job(
                id=j.get("id") or j.get("_id",""),
                title=j("text"),
                company=company,
                url=j("hostedUrl"),
                location=(j.get("categories") or {}).get("location"),
                source="lever",
            ))
        return jobs