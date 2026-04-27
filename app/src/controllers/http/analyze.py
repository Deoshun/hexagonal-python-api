from typing import Optional

from dateutil import parser
from fastapi import APIRouter, Query

from src.controllers.http.errors import DomainError
from src.core.interactors.analyze import AnalyzeInteractor
from src.datasources.s3_repository import S3LogRepository

router = APIRouter()

@router.get("/analyze")
async def analyze(
    bucket: str = Query(..., description="S3 Bucket name"),
    prefix: Optional[str] = Query(None, description="S3 Prefix/Folder"),
    since: Optional[str] = Query(None),
    threshold: int = Query(3, description="Error count threshold for alert")
):
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
    # Hexagonal Wiring:
    # 1. Instantiate the Adapter (S3)
    repo = S3LogRepository()
    # 2. Inject Adapter into the Interactor (Use Case)
    interactor = AnalyzeInteractor(repo)
    
    # 3. Execute logic
    summary = interactor.execute(bucket=bucket, prefix=prefix, since=since_dt, threshold=threshold)
    
    return {
        "total": summary.total,
        "byService": summary.byService,
        "alert": summary.alert
    }
