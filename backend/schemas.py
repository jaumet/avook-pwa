from pydantic import BaseModel

class PlayAuthResponse(BaseModel):
    signed_url: str
    start_position: int
    title: str
    author: str

class ProgressRequest(BaseModel):
    device_id: str
    position_sec: int

class RecoverRequest(BaseModel):
    owner_pin: str
