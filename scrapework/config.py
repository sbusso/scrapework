import enum
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, BaseSettings

load_dotenv()


class Config(BaseModel):
    S3_ENDPOINT: str = Field(default=os.environ["AWS_ENDPOINT_URL"])
    S3_BUCKET: str = Field(default=os.environ["S3_BUCKET"])
    S3_ACCESS_KEY_ID: str = Field(default=os.environ["AWS_ACCESS_KEY_ID"])
    S3_SECRET_ACCESS_KEY: str = Field(default=os.environ["AWS_SECRET_ACCESS_KEY"])
    TELEGRAM_SENDER_TOKEN: str = Field(default=os.environ["TELEGRAM_SENDER_TOKEN"])


config = Config()


class BackendType(enum.Enum):
    FILE = "file"
    S3 = "s3"


class SpiderConfig(BaseModel):
    # Define configuration fields
    base_url: str
    backend: BackendType = Field(
        BackendType.FILE,
        description="Backend can be either 'file' or 's3'",
    )
    s3_bucket: Optional[str] = None

    def validate(self):
        if self.base_url:
            if not self.base_url.startswith("http"):
                raise ValueError("Base URL must start with http:// or https://")
        else:
            raise ValueError("Base URL not provided")
