from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    min_paragraphs: int = 5
    load_from_github: list[str] | None = None
    load_from_folder: str | None = '/app/gesetze/'

    class Config:
        env_file = '.env'
        # alternativ: json/yaml

settings = Settings()