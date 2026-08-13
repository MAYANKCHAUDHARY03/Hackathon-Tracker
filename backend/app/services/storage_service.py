import os
import shutil
import aiofiles
from typing import Protocol, IO
from fastapi import UploadFile

class StorageBackend(Protocol):
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        ...

class LocalStorageBackend:
    def __init__(self, base_dir: str = "/tmp/hackathon_uploads"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        full_path = os.path.join(self.base_dir, destination_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return full_path

class S3StorageBackend:
    def __init__(self, bucket: str, region: str = "us-east-1"):
        self.bucket = bucket
        self.region = region

    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        # In a real app, you would use aioboto3 here:
        # async with aioboto3.Session().client("s3") as s3:
        #     await s3.upload_fileobj(file.file, self.bucket, destination_path)
        # For this skeleton, we just mock the URL.
        return f"s3://{self.bucket}/{destination_path}"

# Dependency provider
_storage_backend = None

def get_storage() -> StorageBackend:
    global _storage_backend
    if _storage_backend is None:
        if os.environ.get("USE_S3_STORAGE") == "true":
            _storage_backend = S3StorageBackend(bucket=os.environ.get("S3_BUCKET", "hackathon-uploads"))
        else:
            _storage_backend = LocalStorageBackend()
    return _storage_backend
