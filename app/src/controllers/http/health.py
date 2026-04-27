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
        # Simple call to verify IAM permissions/Network connectivity
        s3 = boto3.client('s3')
        s3.list_buckets() 
        return {"status": "ready"}
    except ClientError as e:
        return Response(
            content=f"S3 connection failed: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception:
        return Response(
            content="Service not ready",
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
