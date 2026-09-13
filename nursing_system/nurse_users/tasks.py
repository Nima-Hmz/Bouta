import os
import time
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings

@shared_task
def clean_temp_uploads():
    """
    Deletes images in TEMP_UPLOAD_DIR that are older than 3 minutes.
    """
    temp_dir = settings.TEMP_UPLOAD_DIR
    expiration_time = datetime.now().timestamp() - 180  # 3 minutes ago

    if not os.path.exists(temp_dir):
        return

    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)

        # Check if it's a file and get its creation time
        if os.path.isfile(file_path):
            file_creation_time = os.path.getctime(file_path)
            if file_creation_time < expiration_time:
                os.remove(file_path)  # Delete old file
                print(f"Deleted: {file_path}")  # Optional logging