# models.py
from tortoise import fields

from app.dependencies.basemodel import BaseModel


class User(BaseModel):
    email = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=128)

    def __str__(self):
        return self.email
