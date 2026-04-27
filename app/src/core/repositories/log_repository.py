from abc import ABC, abstractmethod
from typing import Iterable, Optional


class LogRepository(ABC):
    @abstractmethod
    def get_logs(self, bucket: Optional[str], prefix: Optional[str], path: Optional[str]) -> Iterable[str]:
        """Returns an iterable of raw log lines (streaming)."""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        pass
