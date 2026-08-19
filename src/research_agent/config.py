from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # AI — LLM
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""   # empty = default OpenAI
    OPENAI_MODEL_NAME: str = ""

    # AI — Embedding (can use a separate endpoint/key)
    EMBEDDING_API_KEY: str = ""          # if empty, falls back to OPENAI_API_KEY
    EMBEDDING_BASE_URL: str = ""         # if empty, falls back to OPENAI_BASE_URL
    EMBEDDING_MODEL_NAME: str = "v_search"
    EMBEDDING_DIM: int = 1024   # 0 = use model's native dim (no dimensions param)

    # File upload
    MAX_FILE_SIZE_MB: int = 7

    # ── computed props ────────────────────────────────────────────────────────
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
