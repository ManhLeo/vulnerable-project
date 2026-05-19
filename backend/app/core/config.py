from __future__ import annotations

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Vulnerability Detection API")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    api_v1_prefix: str = Field(default="/api/v1")

    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="vuln_scanner")
    mongodb_server_selection_timeout_ms: int = Field(default=2000)
    mongodb_connect_timeout_ms: int = Field(default=2000)
    mongodb_socket_timeout_ms: int = Field(default=2000)
    use_in_memory_repository: bool = Field(default=False)

    model_name_or_path: str = Field(default="microsoft/codebert-base")
    model_device: str = Field(default="cpu")
    model_vulnerability_threshold: float = Field(default=0.8)

    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024)

    log_level: str = Field(default="INFO")

    cors_allowed_origins_raw: str = Field(default="http://localhost:3000")
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    cors_allow_headers: list[str] = Field(
        default=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"]
    )

    @computed_field(return_type=list[str])
    @property
    def cors_allowed_origins(self) -> list[str]:
        parsed = [
            origin.strip()
            for origin in self.cors_allowed_origins_raw.split(",")
            if origin.strip()
        ]

        if not parsed:
            parsed = ["http://localhost:3000"] if self.app_env != "production" else []

        if self.app_env == "production":
            parsed = [origin for origin in parsed if origin != "*"]

        return parsed

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
