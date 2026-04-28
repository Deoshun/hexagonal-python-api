import argparse
import json

from src.core.interactors.analyze import AnalyzeInteractor
from src.core.utils.main import parse_time
from src.datasources.file_repository import FileLogRepository
from src.datasources.s3_repository import S3LogRepository


def main():
    parser = argparse.ArgumentParser(description="Log Analytics CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bucket", help="S3 Bucket name")
    group.add_argument("--file", help="Local path to a .jsonl file")
    
    parser.add_argument("--prefix", help="S3 Prefix", default=None)
    parser.add_argument("--since", help="Filter logs since (ISO)", default=None)
    parser.add_argument("--threshnew", type=int, default=3)

    args = parser.parse_args()
    since_dt = parse_time(args.since) if args.since else None

    if args.file:
        repo = FileLogRepository()
        source = args.file
    else:
        repo = S3LogRepository()
        source = args.bucket

    interactor = AnalyzeInteractor(repo)
    summary = interactor.execute(
        prefix=args.prefix,
        since=since_dt,
        threshnew=args.threshnew
    )

    print(json.dumps(summary.__dict__, indent=2))
