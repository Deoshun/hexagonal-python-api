from src.core.repositories.log_repository import LogRepository


class LogRepositoryStub(LogRepository):
    def __init__(self, lines_to_yield):
        self.lines_to_yield = lines_to_yield

    def get_logs(self, source, prefix=None, since=None):
        for line in self.lines_to_yield:
            yield line
    
    def is_healthy(self):
        return True
