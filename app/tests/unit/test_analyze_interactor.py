import json
from datetime import datetime, timezone

from src.core.interactors.analyze import AnalyzeInteractor
from tests.stubs.log_repository_stub import LogRepositoryStub


def test_analyze_aggregates_errors_correctly():
    
    logs = [
        json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "INFO", "service": "auth"}),
        json.dumps({"ts": "2025-09-15T10:01:00Z", "level": "ERROR", "service": "auth"}),
        json.dumps({"ts": "2025-09-15T10:02:00Z", "level": "ERROR", "service": "payments"}),
        json.dumps({"ts": "2025-09-15T10:03:00Z", "level": "ERROR", "service": "auth"}),
    ]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)

    
    summary = interactor.execute(bucket="test", prefix=None, threshold=2)

    
    assert summary.total == 3
    assert summary.byService["auth"] == 2
    assert summary.byService["payments"] == 1
    assert summary.alert is True

def test_analyze_filters_by_since_timestamp():
    
    logs = [
        json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "ERROR", "service": "auth"}), 
        json.dumps({"ts": "2025-09-15T12:00:00Z", "level": "ERROR", "service": "auth"}), 
    ]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)
    since_dt = datetime(2025, 9, 15, 11, 0, tzinfo=timezone.utc)

    
    summary = interactor.execute(bucket="test", prefix=None, since=since_dt)

    
    assert summary.total == 1
    assert summary.byService["auth"] == 1

def test_analyze_handles_malformed_json_gracefully():
    
    logs = ["{ invalid json }", json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "ERROR", "service": "api"})]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)

    
    summary = interactor.execute(bucket="test", prefix=None)

    
    assert summary.parseErrors == 1
    assert summary.total == 1
