from typing import Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)
    LEFT_SIDE_TASK_LIST: list[int] = []
    AIRDROP_CODE_LIST: list[str] = []

settings = Settings()