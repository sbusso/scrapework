import enum
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

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
    META = "meta"


class PipelineConfig(BaseModel):
    base_url: str
    backend: BackendType
    s3_bucket: str
    filename: str
