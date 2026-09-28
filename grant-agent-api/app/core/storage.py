import os
import shutil
import uuid
from typing import Optional, Tuple
from app.core.config import settings

# Attempt GCS import
try:
    from google.cloud import storage as gcs_storage
    HAS_GCS = True
except ImportError:
    HAS_GCS = False

class StorageManager:
    def __init__(self):
        self.local_dir = settings.STORAGE_DIR
        self.screenshots_dir = settings.SCREENSHOTS_DIR
        os.makedirs(self.local_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.gcs_client = None
        if HAS_GCS and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                self.gcs_client = gcs_storage.Client(project=settings.GCP_PROJECT_ID)
            except Exception:
                self.gcs_client = None

    async def save_file(self, content: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[str, str]:
        """
        Saves a file to GCS or local directory.
        Returns: (file_url_or_path, unique_key)
        """
        unique_key = f"{uuid.uuid4().hex}_{filename}"
        local_path = os.path.join(self.local_dir, unique_key)
        
        # Save local copy
        with open(local_path, "wb") as f:
            f.write(content)
            
        if self.gcs_client and settings.GCS_BUCKET_NAME:
            try:
                bucket = self.gcs_client.bucket(settings.GCS_BUCKET_NAME)
                blob = bucket.blob(unique_key)
                blob.upload_from_string(content, content_type=content_type)
                return f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/{unique_key}", unique_key
            except Exception:
                pass
                
        return local_path, unique_key

    async def save_screenshot(self, content: bytes, session_id: str, step_name: str) -> str:
        """Saves a browser session screenshot."""
        filename = f"{session_id}_{step_name}_{uuid.uuid4().hex[:6]}.png"
        local_path = os.path.join(self.screenshots_dir, filename)
        with open(local_path, "wb") as f:
            f.write(content)
        return local_path

storage_manager = StorageManager()
