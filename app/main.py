# main.py
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise

from app.config import config
from app.routers import camera, report, user

app = FastAPI()

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


BASE_DIR = Path(__file__).resolve().parent
app.mount(
    "/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static"
)


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={
        "models": [
            "app.models.user",
            "app.models.camera",
            "app.models.report",
            "app.models.video_analysis",
        ]
    },
    generate_schemas=True,
    add_exception_handlers=True,
)


app.include_router(user.router)
app.include_router(camera.router)
app.include_router(report.router)


@app.get("/")
async def read_root(request: Request, response_class=HTMLResponse):
    print(config.TEMPLATES_DIR, "asd")
    return templates.TemplateResponse(
        "home.html", {"request": {"request": request, "name": "name"}}
    )
