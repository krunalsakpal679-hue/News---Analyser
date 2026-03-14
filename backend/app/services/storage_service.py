# backend/app/services/storage_service.py
"""
Service for file storage operations using Boto3 (compatible with S3 and MinIO).
"""
import os
import tempfile
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.config import settings

class StorageService:
    def __init__(self):
        self._s3 = None
        self.bucket = settings.MINIO_BUCKET

    @property
    def s3(self):
        if self._s3 is None:
            self._s3 = boto3.client(
                's3',
                endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version='s3v4', connect_timeout=2, retries={'max_attempts': 1}),
                region_name='us-east-1' # dummy region for MinIO
            )
        return self._s3

    def _ensure_bucket(self):
        """Creates the bucket if it doesn't already exist."""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except Exception:
            if settings.ENVIRONMENT == "development":
                print(f"WARNING: Could not connect to storage endpoint ({settings.MINIO_ENDPOINT}). Skipping bucket check for development.")
                return
            try:
                self.s3.create_bucket(Bucket=self.bucket)
            except ClientError:
                raise

    async def upload_file(self, job_id: str, filename: str, file_bytes: bytes) -> str:
        """Uploads a file and returns the storage key."""
        key = f"{job_id}/{filename}"
        try:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_bytes
            )
        except Exception:
            if settings.ENVIRONMENT == "development":
                # Fallback to local storage
                local_path = os.path.join(tempfile.gettempdir(), key.replace("/", "_"))
                with open(local_path, "wb") as f:
                    f.write(file_bytes)
                print(f"WARNING: S3 upload failed. Stored locally at {local_path}")
                return f"local://{local_path}"
            raise
        return key

    async def download_file(self, storage_key: str) -> bytes:
        """Downloads a file from storage."""
        if storage_key.startswith("local://"):
            local_path = storage_key.replace("local://", "")
            with open(local_path, "rb") as f:
                return f.read()
        
        response = self.s3.get_object(Bucket=self.bucket, Key=storage_key)
        return response['Body'].read()

    async def get_presigned_url(self, storage_key: str, expiry: int = 3600) -> str:
        """Generates a presigned URL for temporary access to the file."""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': storage_key},
            ExpiresIn=expiry
        )

    async def delete_file(self, storage_key: str) -> bool:
        """Deletes a file from storage."""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=storage_key)
            return True
        except ClientError:
            return False

# Global instance
storage_service = StorageService()
