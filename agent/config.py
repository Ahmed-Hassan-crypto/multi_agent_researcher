"""Centralized configuration for the multi-agent research system."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration."""
    
    tavily_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    max_search_results: int = 10
    max_revision_attempts: int = 3
    llm_temperature: float = 0.0
    llm_model: str = "gemini-2.0-flash"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        return cls(
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", "10")),
            max_revision_attempts=int(os.getenv("MAX_REVISION_ATTEMPTS", "3")),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
            llm_model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY is required")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        return True


_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
