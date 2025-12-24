from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    run_root: Path = Path("runs")
    evaluator_prompt_path: Path = Path("backend/app/core/evaluator_prompt/hqcat_v1.txt")
    request_timeout_seconds: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
