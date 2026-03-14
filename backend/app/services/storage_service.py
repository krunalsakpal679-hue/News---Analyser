import os
import boto3
from botocore.client import Config
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config import settings

class StorageService:
    """
    Unified storage service.
    Uses Cloudinary when CLOUDINARY_CLOUD_NAME is set,
    falls back to MinIO/S3 for local development.
    """
    
    def __init__(self):
        self.use_cloudinary = bool(settings.CLOUDINARY_CLOUD_NAME)
        self._s3 = None
        
        if self.use_cloudinary:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )
        else:
            # S3 client is only initialized if needed
            pass

    @property
    def s3(self):
        if self._s3 is None and not self.use_cloudinary:
            self._s3 = boto3.client(
                's3',
                endpoint_url=f'http://{settings.MINIO_ENDPOINT}',
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version='s3v4', connect_timeout=5, retries={'max_attempts': 1}),
                region_name='us-east-1'
            )
        return self._s3
    
    async def upload_file(self, job_id: str, filename: str, file_bytes: bytes) -> str:
        """Upload file and return storage key/URL."""
        key = f"{job_id}/{filename}"
        
        try:
            if self.use_cloudinary:
                import tempfile
                ext = os.path.splitext(filename)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                try:
                    result = cloudinary.uploader.upload(
                        tmp_path,
                        public_id=key.replace('/', '_'),
                        resource_type='raw',
                        folder='newsense'
                    )
                    return result['public_id']
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            else:
                self.s3.put_object(
                    Bucket=settings.MINIO_BUCKET,
                    Key=key,
                    Body=file_bytes
                )
                return key
        except Exception as e:
            print(f"CRITICAL: Storage upload failed: {str(e)}")
            raise
    
    async def download_file(self, storage_key: str) -> bytes:
        """Download file bytes from storage."""
        try:
            if self.use_cloudinary:
                import httpx
                url = cloudinary.utils.cloudinary_url(storage_key, resource_type='raw', sign_url=True)[0]
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return resp.content
            else:
                response = self.s3.get_object(
                    Bucket=settings.MINIO_BUCKET, 
                    Key=storage_key
                )
                return response['Body'].read()
        except Exception as e:
            print(f"CRITICAL: Storage download failed: {str(e)}")
            raise
    
    async def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage."""
        try:
            if self.use_cloudinary:
                cloudinary.uploader.destroy(storage_key, resource_type='raw')
            else:
                self.s3.delete_object(
                    Bucket=settings.MINIO_BUCKET, 
                    Key=storage_key
                )
            return True
        except Exception:
            return False

# Global instance
storage_service = StorageService()
