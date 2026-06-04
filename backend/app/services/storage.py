from pathlib import Path
from uuid import UUID

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.root = self.settings.storage_root
        self.root.mkdir(parents=True, exist_ok=True)
        self._s3 = None
        if self.settings.use_s3:
            self._s3 = boto3.client(
                "s3",
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key,
                region_name=self.settings.aws_region,
            )

    def job_dir(self, job_id: UUID) -> Path:
        path = self.root / "jobs" / str(job_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_upload(self, job_id: UUID, filename: str, data: bytes) -> str:
        dest = self.job_dir(job_id) / filename
        dest.write_bytes(data)
        return str(dest)

    def local_path(self, relative_or_absolute: str) -> Path:
        p = Path(relative_or_absolute)
        if p.is_absolute():
            return p
        return self.root / relative_or_absolute

    def get_download_url(self, file_path: str) -> str | None:
        if not self.settings.use_s3 or not self._s3:
            return None
        key = file_path.replace(str(self.root) + "/", "")
        try:
            return self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.settings.s3_bucket, "Key": key},
                ExpiresIn=3600,
            )
        except ClientError:
            return None

    def upload_to_s3(self, local_path: Path, key: str) -> str | None:
        if not self._s3:
            return str(local_path)
        self._s3.upload_file(str(local_path), self.settings.s3_bucket, key)
        return f"s3://{self.settings.s3_bucket}/{key}"
