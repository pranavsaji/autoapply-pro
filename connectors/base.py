from abc import ABC, abstractmethod
from typing import List
from apps.api.models.domain import Job

class JobConnector(ABC):
    @abstractmethod
    def search(self, query: str, locations: list[str]) -> List[Job]:
        ...