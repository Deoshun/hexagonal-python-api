from dateutil import parser

from src.controllers.http.errors import DomainError


def parse_time(since):
    since_dt = None
    if since:
        try:
            # This handles '2025-09-15', '2025-09-15T14:00', etc.
            since_dt = parser.parse(since)
            # Ensure it's timezone aware if your logs are (usually UTC)
            if since_dt.tzinfo is None:
                from datetime import timezone
                since_dt = since_dt.replace(tzinfo=timezone.utc)
        except ValueError as err:
            raise DomainError("Invalid date format for 'since'.") from err
    return since_dt
