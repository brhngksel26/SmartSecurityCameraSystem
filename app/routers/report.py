import os

import aiofiles
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager

from app.config import config
from app.models.report import Report
from app.models.video_analysis import VideoAnalysis
from app.utils.auth import AuthHandler
from app.utils.task import process_video_task

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
login_manager = LoginManager(config.SECRET_KEY, token_url="/token")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
auth_handler = AuthHandler()


@router.get("/reports", response_class=HTMLResponse)
async def get_reports(request: Request, email=Depends(auth_handler.auth_wrapper)):
    reports = await Report.all().prefetch_related("camera")
    return templates.TemplateResponse(
        "report.html", {"request": request, "reports": reports}
    )


@router.get("/reports/{report_id}", response_class=HTMLResponse)
async def get_report(
    request: Request, report_id: int, email=Depends(auth_handler.auth_wrapper)
):
    report = await Report.get(id=report_id).prefetch_related(
        "camera", "objects_detected", "anomalies_detected"
    )
    return templates.TemplateResponse(
        "report_detail.html", {"request": request, "report": report}
    )


@router.post("/reports/delete/{report_id}", response_class=HTMLResponse)
async def delete_report(
    request: Request, report_id: int, email=Depends(auth_handler.auth_wrapper)
):
    report = await Report.get(id=report_id)
    await report.delete()
    return RedirectResponse(url="/reports", status_code=302)


@router.get("/read_form", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("upload_video.html", {"request": request})


@router.post("/upload/")
async def upload_video(video: UploadFile = File(...)):
    video_path = os.path.join(config.UPLOAD_DIRECTORY, video.filename)

    # Save the uploaded video file
    async with aiofiles.open(video_path, "wb") as out_file:
        content = await video.read()
        await out_file.write(content)

    video_analysis = await VideoAnalysis.create(
        filename=video.filename,
        file_path=config.UPLOAD_DIRECTORY,
        report_type="Video Analysis",
        summary="Anlık video analizi",
    )

    process_video_task.delay(video_analysis.id)

    return RedirectResponse(url="/", status_code=303)
