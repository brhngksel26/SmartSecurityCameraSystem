from pydantic import BaseModel

from app.dependencies.baseschema import BaseResponse


class CameraBase(BaseModel):
    location: str
    ip_address: str
    is_active: bool = True


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    location: str = None
    ip_address: str = None
    is_active: bool = None


class CameraResponse(CameraBase, BaseResponse):
    id: int

    class Config:
        orm_mode = True
