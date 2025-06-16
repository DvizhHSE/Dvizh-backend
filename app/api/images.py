from fastapi import APIRouter, UploadFile, File, HTTPException, status
from PIL import Image
import boto3
from dotenv import load_dotenv
import io
import os
import uuid
from fastapi.responses import FileResponse

router = APIRouter(tags=["Images"])

load_dotenv()

# Backblaze B2 Credentials from environment variables
KEY_ID = os.getenv("BACKBLAZE_KEY_ID")
APPLICATION_KEY = os.getenv("BACKBLAZE_APPLICATION_KEY")
ENDPOINT_URL = os.getenv("BACKBLAZE_ENDPOINT_URL")
BUCKET_NAME = os.getenv("BACKBLAZE_BUCKET_NAME")

# Initialize B2 client
s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=KEY_ID,
    aws_secret_access_key=APPLICATION_KEY,
    config=boto3.session.Config(signature_version='v4', s3={'checksum_algorithm': None}) #Попробуем отключить совсем
)

@router.patch("/upload-picture")
async def upload_profile_picture(file: UploadFile = File(...)):
    """
    Загружает изображение профиля пользователя в Backblaze B2,
    обрабатывает его и возвращает ссылку на изображение.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        file_name = f"{uuid.uuid4()}.{image.format.lower()}"
        try:
            s3_client.upload_fileobj(
                io.BytesIO(contents),
                BUCKET_NAME,
                file_name,
                ExtraArgs={"ContentType": file.content_type}, 
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to B2: {e}",
            )

        # Construct the image URL
        image_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{file_name}"

        return {"profile_picture": image_url}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))