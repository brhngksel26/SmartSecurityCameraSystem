from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager

from app.config import config
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate
from app.utils.auth import AuthHandler
from app.utils.task import process_camera_task

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
login_manager = LoginManager(config.SECRET_KEY, token_url="/token")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
auth_handler = AuthHandler()


@router.get("/cameras/", response_class=HTMLResponse)
async def get_cameras(request: Request, email=Depends(auth_handler.auth_wrapper)):
    cameras = await Camera.all()
    return templates.TemplateResponse(
        "camera.html", {"request": request, "camera": cameras}
    )


@router.post(
    "/cameras/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED
)
async def create_camera(
    request: Request, camera: CameraCreate, email=Depends(auth_handler.auth_wrapper)
):
    new_camera = await Camera.create(**camera.dict())
    if camera.is_active == True:
        task = process_camera_task.delay(camera_id=new_camera.id)
        camera.task_id = task.id
    return templates.TemplateResponse(
        "camera_detail.html", {"request": request, "camera": camera}
    )


@router.get("/cameras/{camera_id}", response_class=HTMLResponse)
async def get_camera(
    request: Request, camera_id: int, email=Depends(auth_handler.auth_wrapper)
):
    camera = await Camera.get_or_none(id=camera_id)
    if not camera:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": ""}
        )
    return templates.TemplateResponse(
        "camera_detail.html", {"request": request, "camera": camera}
    )


@router.put("/cameras/{camera_id}", response_class=HTMLResponse)
async def update_camera(
    request: Request,
    camera_id: int,
    camera_data: CameraUpdate,
    email=Depends(auth_handler.auth_wrapper),
):
    camera = await Camera.get_or_none(id=camera_id)
    if not camera:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": ""}
        )

    camera_data_dict = camera_data.dict(exclude_unset=True)
    for key, value in camera_data_dict.items():
        setattr(camera, key, value)

    if not old_is_active and camera.is_active:
        task = process_camera_task.delay(camera_id=camera.id)
        camera.task_id = task.id

    if old_is_active and not camera.is_active and camera.task_id:
        celery_app.control.revoke(camera.task_id, terminate=True)
        camera.task_id = None

    await camera.save()
    return templates.TemplateResponse(
        "cameras_detail.html", {"request": request, "camera": camera}
    )


@router.post("/cameras/{camera_id}/delete/", response_class=HTMLResponse)
async def delete_camera(
    request: Request, camera_id: int, email=Depends(auth_handler.auth_wrapper)
):
    camera = await Camera.get_or_none(id=camera_id)
    if not camera:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Camera not found."}
        )

    await camera.delete()
    return templates.TemplateResponse(
        "cameras.html", {"request": request, "message": "Camera deleted successfully."}
    )
