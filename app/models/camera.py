from tortoise import fields

from app.dependencies.basemodel import BaseModel


class Camera(BaseModel):
    location = fields.CharField(max_length=255, null=False)
    ip_address = fields.CharField(max_length=255, null=False)
    is_active = fields.BooleanField(default=True)
    task_id = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Camera(location={self.location}, ip_address={self.ip_address}, is_active={self.is_active})"
