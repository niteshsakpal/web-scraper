import uuid

import boto3
from django.conf import settings


class S3StorageService:
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            region_name=settings.AWS_DEFAULT_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    def upload_html(self, html: str, job_id: int) -> str:
        key = f"jobs/{job_id}/raw/{uuid.uuid4()}.html"
        self._client.put_object(Bucket=self.bucket, Key=key, Body=html.encode("utf-8"), ContentType="text/html")
        return f"s3://{self.bucket}/{key}"
