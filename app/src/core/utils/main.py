from dateutil import parser

from src.controllers.http.errors import DomainError


def parse_time(since):
    since_dt = None
    if since:
        try:
            
            since_dt = parser.parse(since)
            
            if since_dt.tzinfo is None:
                from datetime import timezone
                since_dt = since_dt.replace(tzinfo=timezone.utc)
        except ValueError as err:
            raise DomainError("Invalid date format for 'since'.") from err
    return since_dt
