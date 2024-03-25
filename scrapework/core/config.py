import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class EnvConfig(BaseModel):
    @classmethod
    def create_config(cls):
        fields = {}
        for field_name, field_value in cls.model_fields.items():
            if field_name in os.environ:
                fields[field_name] = os.environ[field_name]
            else:
                raise ValueError(
                    f"Required environment variable '{field_name}' not set"
                )

        return cls(**fields)


config = EnvConfig()

SCRAPEOPS_API_KEY: Optional[str] = Field(default=os.environ.get("SCRAPEOPS_API_KEY"))


class PipelineConfig(BaseModel):
    base_url: str
    filename: str
