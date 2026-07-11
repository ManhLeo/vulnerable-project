from __future__ import annotations

from pydantic import AliasChoices, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


class Settings(BaseSettings):
    app_name: str = Field(default="Vulnerability Detection API")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    api_v1_prefix: str = Field(default="/api/v1")

    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        validation_alias=AliasChoices("MONGODB_URL", "MONGODB_URI", "mongodb_uri"),
    )
    mongodb_db_name: str = Field(
        default="vuln_scanner",
        validation_alias=AliasChoices("MONGODB_DB_NAME", "mongodb_db_name"),
    )
    mongodb_server_selection_timeout_ms: int = Field(default=5000)
    mongodb_connect_timeout_ms: int = Field(default=5000)
    mongodb_socket_timeout_ms: int = Field(default=10000)
    mongodb_max_pool_size: int = Field(default=50)
    mongodb_scans_collection: str = Field(default="scans")

    jwt_secret_key: str = Field(
        default=DEFAULT_JWT_SECRET_KEY,
        validation_alias=AliasChoices("JWT_SECRET_KEY")
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=24 * 60) # 24 hours
    admin_email: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ADMIN_EMAIL"),
    )
    admin_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ADMIN_PASSWORD"),
    )
    bcrypt_rounds: int = Field(default=12, validation_alias=AliasChoices("BCRYPT_ROUNDS", "bcrypt_rounds"))
    use_in_memory_repository: bool = Field(default=False)
    max_request_body_size: int = Field(
        default=10 * 1024 * 1024,
        validation_alias=AliasChoices("MAX_REQUEST_BODY_SIZE", "max_request_body_size"),
    )  # 10 MB global limit

    model_name_or_path: str = Field(default="microsoft/codebert-base")
    model_device: str = Field(default="cpu")
    model_vulnerability_threshold: float = Field(default=0.8)

    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024)

    log_level: str = Field(default="INFO")

    cors_allowed_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS_RAW"),
    )
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
            parsed = ["http://localhost:3000", "http://127.0.0.1:3000"] if self.app_env != "production" else []

        if self.app_env == "production":
            parsed = [origin for origin in parsed if origin != "*"]

        return parsed

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.app_env.lower() == "production":
            if not self.jwt_secret_key or self.jwt_secret_key == DEFAULT_JWT_SECRET_KEY:
                raise ValueError("JWT_SECRET_KEY must be set to a strong non-default value in production")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=("settings_",),
    )


settings = Settings()
