from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Summary:
    total: int = 0
    byService: Dict[str, int] = field(default_factory=dict)
    parseErrors: int = 0
    threshnew: int = 0

    @property
    def alert(self) -> bool:
        return self.total >= self.threshnew

    def add_error(self, service: str):
        self.total += 1
        self.byService[service] = self.byService.get(service, 0) + 1

    def add_parse_error(self):
        self.parseErrors += 1
