from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    model_id: str = Field(default="sshleifer/tiny-gpt2", alias="MODEL_ID")
    device: str = Field(default="auto", alias="DEVICE")
    torch_dtype: str = Field(default="auto", alias="TORCH_DTYPE")
    max_input_tokens: int = Field(default=2048, alias="MAX_INPUT_TOKENS")
    default_max_new_tokens: int = Field(default=64, alias="DEFAULT_MAX_NEW_TOKENS")


settings = Settings()

