import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.server.app import app

client = TestClient(app)

def test_analyze_endpoint_success():
    with patch("src.controllers.http.analyze.S3LogRepository") as mock_repo:
        instance = mock_repo.return_value
        instance.get_logs.return_value = iter([
            json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "ERROR", "service": "web"})
        ])

        response = client.get("/analyze?bucket=my-bucket&threshnew=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["alert"] is True

def test_analyze_endpoint_missing_bucket():
    response = client.get("/analyze")
    assert response.status_code == 422
