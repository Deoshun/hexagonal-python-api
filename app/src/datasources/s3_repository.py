import re
from datetime import datetime, timezone

import boto3

from src.core.repositories.log_repository import LogRepository


class S3LogRepository(LogRepository):
    def __init__(self):
        self.client = boto3.client('s3')

    def _parse_filename_to_date(self, filename: str) -> datetime:
            
            match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})', filename)
            if match:
                
                
                dt = datetime.strptime(match.group(1), "%Y-%m-%dT%H-%M")
                return dt.replace(tzinfo=timezone.utc)
            return None

    def get_logs(self, bucket: str, prefix: str = None, since: datetime = None):
        paginator = self.client.get_paginator('list_objects_v2')
        operation_parameters = {'Bucket': bucket}
        if prefix:
            operation_parameters['Prefix'] = prefix

        for page in paginator.paginate(**operation_parameters):
            for obj in page.get('Contents', []):
                key = obj['Key']
                filename = key.split('/')[-1] 


                file_date = self._parse_filename_to_date(filename)

                if since and file_date and file_date < since:
                    if file_date.date() < since.date(): 
                        continue

                if key.endswith('/'): 
                    continue

                
                streaming_body = self.client.get_object(Bucket=bucket, Key=key)['Body']
                for line in streaming_body.iter_lines():
                    if line: 
                        yield line.decode('utf-8')
    
    def is_healthy(self) -> bool:
        try:
            self.client.list_buckets()
            return True
        except Exception:
            return False
