import json
from datetime import datetime, timezone

from src.core.interactors.analyze import AnalyzeInteractor
from tests.stubs.log_repository_stub import LogRepositoryStub


def test_analyze_aggregates_errors_correctly():
    # GIVEN: Logs with mixed levels and services
    logs = [
        json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "INFO", "service": "auth"}),
        json.dumps({"ts": "2025-09-15T10:01:00Z", "level": "ERROR", "service": "auth"}),
        json.dumps({"ts": "2025-09-15T10:02:00Z", "level": "ERROR", "service": "payments"}),
        json.dumps({"ts": "2025-09-15T10:03:00Z", "level": "ERROR", "service": "auth"}),
    ]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)

    # WHEN: Executing analysis with threshold 2
    summary = list(interactor.execute(bucket="test", prefix=None, threshold=2))[-1]

    # THEN: Totals should match and alert should trigger
    assert summary.total == 3
    assert summary.byService["auth"] == 2
    assert summary.byService["payments"] == 1
    assert summary.alert is True

def test_analyze_filters_by_since_timestamp():
    # GIVEN: Logs spanning across a specific time
    logs = [
        json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "ERROR", "service": "auth"}), # OLD
        json.dumps({"ts": "2025-09-15T12:00:00Z", "level": "ERROR", "service": "auth"}), # NEW
    ]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)
    since_dt = datetime(2025, 9, 15, 11, 0, tzinfo=timezone.utc)

    # WHEN: Analyzing with 'since' filter
    summary = list(interactor.execute(bucket="test", prefix=None, since=since_dt))[-1]

    # THEN: Only the log after 11:00 should be counted
    assert summary.total == 1
    assert summary.byService["auth"] == 1

def test_analyze_handles_malformed_json_gracefully():
    # GIVEN: A log line that isn't valid JSON
    logs = ["{ invalid json }", json.dumps({"ts": "2025-09-15T10:00:00Z", "level": "ERROR", "service": "api"})]
    stub_repo = LogRepositoryStub(logs)
    interactor = AnalyzeInteractor(stub_repo)

    # WHEN: Analyzing
    summary = list(interactor.execute(bucket="test", prefix=None))[-1]

    # THEN: It should record the parse error and continue to the valid line
    assert summary.parseErrors == 1
    assert summary.total == 1
