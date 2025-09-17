from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VideoBase(BaseModel):
    filename: str
    duration: float
    size: int

class VideoCreate(VideoBase):
    filepath: str

class Video(VideoBase):
    id: int
    upload_time: datetime

    class Config:
        orm_mode = True

class TrimRequest(BaseModel):
    video_id: int
    start_time: float
    end_time: float

# Add these at the end of the file
class TextOverlayRequest(BaseModel):
    video_id: int
    text: str
    start_time: int
    end_time: int

class WatermarkRequest(BaseModel):
    video_id: int