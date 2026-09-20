# alpha_hook/src/settings.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, PostgresDsn, AmqpDsn, Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    Настройки для alpha_hook сервиса.
    Переменные берутся из:
    1. Корневого .env (общие настройки)
    2. ./alpha_hook/.env (специфичные для сервиса)
    """

    # === PostgreSQL ===
    # Эти переменные должны быть в корневом .env
    postgres_user: str
    postgres_password: str
    postgres_db: str
    app_reader_user: str
    app_reader_password: str

    # Хосты и порты (фиксированы внутри Docker)
    postgres_host: str = Field("pg-master", alias="POSTGRES_HOST")
    postgres_port: str = Field("5432", alias="POSTGRES_PORT")
    postgres_replica_host: str = Field("pg-replica", alias="POSTGRES_REPLICA_HOST")
    postgres_replica_port: str = Field("5432", alias="POSTGRES_REPLICA_PORT")

    # === RabbitMQ ===
    rabbitmq_default_user: str = Field(alias="RABBITMQ_DEFAULT_USER")
    rabbitmq_default_pass: str = Field(alias="RABBITMQ_DEFAULT_PASS")
    rabbitmq_host: str = Field("rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: str = Field("5672", alias="RABBITMQ_PORT")

    # === Alfa Bank ===
    # Берётся из alpha_hook/.env
    alfa_secret_key: Optional[str] = Field(None, alias="ALFA_SECRET_KEY")
    alfa_test_mode: bool = Field(True, alias="ALFA_TEST_MODE")

    # === Логирование ===
    log_dir: Path = Field("/app/logs", alias="LOG_DIR")

    # === Строгая валидация ===
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # === Производные свойства ===
    @property
    def database_write_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=int(self.postgres_port),
            path=self.postgres_db,
        )

    @property
    def database_read_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.app_reader_user,
            password=self.app_reader_password,
            host=self.postgres_replica_host,
            port=int(self.postgres_replica_port),
            path=self.postgres_db,
        )

    @property
    def rabbitmq_url(self) -> AmqpDsn:
        return AmqpDsn.build(
            scheme="amqp",
            username=self.rabbitmq_default_user,
            password=self.rabbitmq_default_pass,
            host=self.rabbitmq_host,
            port=int(self.rabbitmq_port),
            path="/",
        )


settings = Settings()