from pathlib import Path


class Config:
    DATABASE_URL = "sqlite://db.sqlite3"
    SECRET_KEY = "0auFzYdG8EOOx0a4YEL9a19J0eW-I9z-7eWCaAJ-mO1cZkIDFaQQtHbPX0uXPqgEp_JajdKMZg8zFs05nxNEOg"

    TORTOISE_ORM = {
        "connections": {"default": DATABASE_URL},
        "apps": {
            "models": {
                "models": ["models.user"],
                "default_connection": "default",
            },
        },
    }

    BASE_DIR = Path(__file__).resolve().parent
    TEMPLATES_DIR = Path(BASE_DIR, "templates")


# Örnek kullanım
config = Config()
