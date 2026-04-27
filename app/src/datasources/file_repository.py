import os

from src.core.repositories.log_repository import LogRepository


class FileLogRepository(LogRepository):
    def get_logs(self, file_path: str, prefix: str = None, since=None):
        """
        In this adapter, 'file_path' acts as the bucket/source.
        'prefix' is ignored for single files, but could be used for directories.
        """
        if not os.path.exists(file_path):
            from src.controllers.http.errors import ResourceNotFound
            raise ResourceNotFound(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    yield line
