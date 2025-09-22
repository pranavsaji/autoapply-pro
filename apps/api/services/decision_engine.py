from typing import List
from ..models.domain import Job, Profile

class DecisionEngine:
    def __init__(self, prefs: dict):
        self.prefs = prefs

    def score(self, profile: Profile, job: Job) -> float:
        score = 0.0
        for inc in self.prefs.get("role_titles", {}).get("include", []):
            if inc.lower() in job.title.lower():
                score += 0.4
        locs = self.prefs.get("locations", {}).get("preferred", [])
        if not locs or (job.location and any(l.lower() in job.location.lower() for l in locs)):
            score += 0.3
        # TODO: JD embedding similarity with profile summary/skills
        return min(score, 1.0)

    def filter_rank(self, profile: Profile, jobs: List[Job]) -> List[Job]:
        ranked = sorted(jobs, key=lambda j: self.score(profile, j), reverse=True)
        return [j for j in ranked if self.score(profile, j) >= 0.5]