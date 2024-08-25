from datetime import datetime

from tortoise import fields
from tortoise.models import Model

from app.dependencies.basemodel import BaseModel


class VideoObjectDetection(Model):
    object_class = fields.CharField(max_length=255, null=True)
    confidence = fields.FloatField(null=True)
    bounding_box = fields.JSONField(null=True)
    timestamp = fields.DatetimeField(default=datetime.utcnow)

    class Meta:
        table = "video_object_detections"


class VideoAnomaly(Model):
    detected_at = fields.DatetimeField(default=datetime.utcnow)
    description = fields.CharField(max_length=255, null=True)
    severity = fields.IntField(null=True)

    class Meta:
        table = "video_anomalies"


class VideoAnalysis(BaseModel):
    filename = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=255)
    report_type = fields.CharField(max_length=255, null=True)
    objects_detected = fields.ManyToManyField(
        "models.VideoObjectDetection", related_name="object_detections"
    )
    anomalies_detected = fields.ManyToManyField(
        "models.VideoAnomaly", related_name="anomalies"
    )
    summary = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "videoanalysis"

    def __str__(self):
        return self.filename
