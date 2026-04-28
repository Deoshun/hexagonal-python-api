import json
from datetime import datetime

from dateutil import parser

from src.core.entities.summary import Summary
from src.core.repositories.log_repository import LogRepository


class AnalyzeInteractor:
    def __init__(self, repository: LogRepository):
        self.repository = repository

    def execute(self, bucket, prefix, since: datetime = None, threshold=3) -> Summary:
            summary = Summary(threshold=threshold)
            
            for line in self.repository.get_logs(bucket, prefix, since=since):
                try:
                    data = json.loads(line)
                    log_ts_str = data.get("ts")
                    
                    if since and log_ts_str:
                        
                        log_ts = parser.isoparse(log_ts_str)
                        
                        if log_ts < since:
                            continue

                    if data.get("level") == "ERROR":
                        summary.add_error(data.get("service", "unknown"))
                except Exception:
                    summary.add_parse_error()
                    
            return summary
