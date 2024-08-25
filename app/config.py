from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_URL: str = "sqlite://db.sqlite3"
    SECRET_KEY: str = (
        "0auFzYdG8EOOx0a4YEL9a19J0eW-I9z-7eWCaAJ-mO1cZkIDFaQQtHbPX0uXPqgEp_JajdKMZg8zFs05nxNEOg"
    )

    TORTOISE_ORM: dict = {
        "connections": {"default": DATABASE_URL},
        "apps": {
            "models": {
                "models": [
                    "models.users",
                    "models.camera",
                    "models.reports",
                    "models.videoanalysis",
                ],
                "default_connection": "default",
            },
        },
    }

    MAIL_USERNAME: str = "your-email@example.com"
    MAIL_PASSWORD: str = "your-password"
    MAIL_FROM: str = "your-email@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATES_DIR: Path = Path(BASE_DIR, "templates")
    BOTTLE_MODEL_PATH: Path = Path(BASE_DIR, "files/yolo_model/bottle.pt")
    FIRE_MODEL_PATH: Path = Path(BASE_DIR, "files/yolo_model/fire.pt")
    OBJECT_MODEL_PATH: Path = Path(BASE_DIR, "files/yolo_model/object.pt")
    UPLOAD_DIRECTORY: Path = Path(BASE_DIR, "static/videos")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create an instance of the settings
config = Config()
