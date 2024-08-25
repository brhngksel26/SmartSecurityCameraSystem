from celery import Celery
from tortoise import Tortoise

from app.config import config


async def init_db():
    await Tortoise.init(config=config.TORTOISE_ORM)
    await Tortoise.generate_schemas()


celery_app = Celery(
    name=__name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    result_expires=3600,
)
