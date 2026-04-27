import os

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Response, status

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """
    Liveness probe: Returns 200 if the process is running.
    Used by the ALB to know the container hasn't deadlocked.
    """
    return {"status": "ok"}

@router.get("/readyz")
async def readiness_check():
    """
    Readiness probe: Checks if the app can actually talk to AWS.
    If this fails, the ALB will stop sending traffic to this instance.
    """
    try:
        s3 = boto3.client('s3')
        target_bucket = os.getenv("DEFAULT_BUCKET", "your-default-bucket")
        
        # This only checks the specific bucket you have access to
        s3.head_bucket(Bucket=target_bucket)
        
        return {"status": "ready", "target": target_bucket}
    except ClientError as e:
        return Response(
            content=f"S3 access check failed: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@router.get("/version")
async def get_version():
    """
    Returns the Git SHA injected at build time.
    """
    return {
        "version": os.getenv("APP_VERSION", "development"),
        "environment": os.getenv("APP_ENV", "local")
    }
