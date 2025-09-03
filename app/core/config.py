from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Business control system'
    description: str = 'Система управления и контроля бизнеса'

    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_port: int
    postgres_db: str

    secret: str

    @property
    def database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )

    class Config:
        env_file = '.env'


settings = Settings()
