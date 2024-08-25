from tortoise import run_async

from app.dependencies.celery_app import celery_app
from app.utils.video_processor import VideoProcessor


@celery_app.task(bind=True)
def process_camera_task(self, camera_id):
    run_async(VideoProcessor(source=camera_id, is_camera=True).run_camera())


@celery_app.task(bind=True)
def process_video_task(self, id):
    run_async(VideoProcessor(source=id, is_camera=False).run_video())
