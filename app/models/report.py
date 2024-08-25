from datetime import datetime

from tortoise import fields
from tortoise.models import Model

from app.dependencies.basemodel import BaseModel


class ObjectDetection(Model):
    object_class = fields.CharField(max_length=255, null=True)
    confidence = fields.FloatField(null=True)
    bounding_box = fields.JSONField(null=True)
    timestamp = fields.DatetimeField(default=datetime.utcnow)

    class Meta:
        table = "object_detections"


class Anomaly(Model):
    detected_at = fields.DatetimeField(default=datetime.utcnow)
    description = fields.CharField(max_length=255, null=True)
    severity = fields.IntField(null=True)

    class Meta:
        table = "anomalies"


class Report(BaseModel):
    camera = fields.ForeignKeyField(
        "models.Camera", related_name="reports", on_delete=fields.CASCADE
    )
    report_type = fields.CharField(max_length=255, null=True)
    objects_detected = fields.ManyToManyField(
        "models.ObjectDetection", related_name="object_detections"
    )
    anomalies_detected = fields.ManyToManyField(
        "models.Anomaly", related_name="anomalies"
    )
    summary = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "reports"

    def __str__(self):
        return f"Report(camera={self.camera}, report_type={self.report_type}, summary={self.summary})"
