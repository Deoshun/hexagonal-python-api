# (Optional) Load environment variables for S3 credentials
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# 1. Import the router from your controller
from src.controllers.http.analyze import router as analyze_router
from src.controllers.http.errors import (
    APIErrorMessage,
    DomainError,
    RepositoryError,
    ResourceNotFound,
)
from src.controllers.http.health import router as status_router

load_dotenv()

app = FastAPI(title="Log Analytics Service")

# 2. Register the router
# The 'tags' help group these in the /docs (Swagger) UI
app.include_router(analyze_router, tags=["Analytics"])
app.include_router(status_router, tags=["Health"])

@app.get("/")
async def root():
    return {"status": "Log Analytics Service is running"}

# --- Exception Handlers ---
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    error_msg = APIErrorMessage(type=exc.__class__.__name__, message=str(exc))
    return JSONResponse(status_code=400, content=error_msg.dict())

@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: ResourceNotFound) -> JSONResponse:
    error_msg = APIErrorMessage(type=exc.__class__.__name__, message=str(exc))
    return JSONResponse(status_code=404, content=error_msg.dict())

@app.exception_handler(RepositoryError)
async def repository_error_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    error_msg = APIErrorMessage(
        type=exc.__class__.__name__, message="Internal data source error."
    )
    return JSONResponse(status_code=500, content=error_msg.dict())

@app.exception_handler(Exception)
async def catch_all_handler(request: Request, exc: Exception) -> JSONResponse:
    # This prevents the raw Python stack trace from ever reaching the user
    # Log the real error on the server side for debugging
    print(f"CRITICAL ERROR: {exc}") 
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIErrorMessage(
            type="InternalServerError",
            message="An unexpected error occurred. Please contact support."
        ).dict()
    )

