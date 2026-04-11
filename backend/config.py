"""
JobForge — Configuration
Loads settings from .env file using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Groq AI
    GROQ_API_KEY: str = ""

    # Database - Railway provides DATABASE_URL, else use SQLite
    DATABASE_URL: str = "sqlite:///./data/jobforge.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Scraper defaults
    SCRAPER_DELAY_SECONDS: float = 2.0
    SCRAPER_JITTER_SECONDS: float = 1.0

    # Default search keywords
    DEFAULT_KEYWORDS: str = "data scientist,machine learning engineer,AI intern,NLP engineer,MLOps,deep learning"

    # Greenhouse company slugs
    GREENHOUSE_COMPANIES: str = "anthropic,huggingface,openai,deepmind,databricks,cohere,scale-ai,wandb,neptune-ai,clarifai,snorkel-ai"

    # Lever company slugs
    LEVER_COMPANIES: str = "openai,mistral,together-ai,modal,replicate,langchain,llamaindex"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def default_keywords_list(self) -> List[str]:
        return [kw.strip() for kw in self.DEFAULT_KEYWORDS.split(",")]

    @property
    def greenhouse_companies_list(self) -> List[str]:
        return [slug.strip() for slug in self.GREENHOUSE_COMPANIES.split(",")]

    @property
    def lever_companies_list(self) -> List[str]:
        return [slug.strip() for slug in self.LEVER_COMPANIES.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton
settings = Settings()
