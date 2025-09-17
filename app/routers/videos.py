import shutil
import os
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel # Import BaseModel here

from ..models import models
from ..schemas import schemas
from ..services import video_processing

router = APIRouter()
UPLOAD_DIRECTORY = "media/uploads"
EDIT_DIRECTORY = "media/edits"

# --- Pydantic Models for Level 3 ---
# We define them here for simplicity
class TextOverlayRequest(BaseModel):
    video_id: int
    text: str
    start_time: int
    end_time: int

class WatermarkRequest(BaseModel):
    video_id: int

# --- Background Task (Level 4 & 5) ---
def process_video_qualities(video_id: int):
    db = next(models.get_db())
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        print(f"Background Task Error: Video with ID {video_id} not found.")
        db.close()
        return

    qualities = ["1080p", "720p", "480p"]
    base, ext = os.path.splitext(os.path.basename(video.filepath))
    TRANSCODE_DIR = "media/transcoded"

    if not os.path.exists(TRANSCODE_DIR):
        os.makedirs(TRANSCODE_DIR)

    for quality in qualities:
        output_filename = f"{base}_{quality}{ext}"
        output_path = os.path.join(TRANSCODE_DIR, output_filename)
        result_path = video_processing.transcode_video(video.filepath, output_path, quality)
        if result_path:
            db_quality = models.VideoQuality(
                original_video_id=video_id,
                filepath=result_path,
                quality=quality
            )
            db.add(db_quality)
    
    # When processing is done, update the status to "complete"
    video.status = "complete"
    db.commit()
    print(f"Background task for video ID {video_id} completed.")
    db.close()

# --- API Endpoints ---

@router.post("/upload")
async def upload_video_and_process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(models.get_db)
):
    for directory in [UPLOAD_DIRECTORY, EDIT_DIRECTORY]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    filepath = os.path.join(UPLOAD_DIRECTORY, file.filename)
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="File with this name already exists.")
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    metadata = video_processing.get_video_metadata(filepath)
    if not metadata:
        raise HTTPException(status_code=500, detail="Could not process video metadata.")
        
    video_data = schemas.VideoCreate(filename=file.filename, filepath=filepath, **metadata)
    db_video = models.Video(**video_data.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    background_tasks.add_task(process_video_qualities, db_video.id)

    return JSONResponse(
        status_code=202,
        content={"message": "Video upload accepted, processing has started.", "video_id": db_video.id}
    )

@router.get("/videos", response_model=List[schemas.Video])
def list_videos(db: Session = Depends(models.get_db)):
    return db.query(models.Video).all()

@router.post("/trim", response_class=FileResponse)
async def trim_video_api(
    request_data: schemas.TrimRequest, db: Session = Depends(models.get_db)
):
    video = db.query(models.Video).filter(models.Video.id == request_data.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Original video not found.")
    base, ext = os.path.splitext(video.filename)
    output_filename = f"{base}_trimmed_{request_data.start_time}_{request_data.end_time}{ext}"
    output_path = os.path.join(EDIT_DIRECTORY, output_filename)
    trimmed_file = video_processing.trim_video(
        video.filepath, output_path, request_data.start_time, request_data.end_time
    )
    if not trimmed_file:
        raise HTTPException(status_code=500, detail="Failed to trim video.")
    db_trim = models.TrimmedVideo(
        original_video_id=video.id,
        filepath=trimmed_file,
        start_time=request_data.start_time,
        end_time=request_data.end_time
    )
    db.add(db_trim)
    db.commit()
    return FileResponse(trimmed_file, media_type="video/mp4", filename=output_filename)

@router.post("/overlay/text", response_class=FileResponse)
async def add_text_overlay_api(
    request: TextOverlayRequest, db: Session = Depends(models.get_db)
):
    """Adds a text overlay to a video."""
    video = db.query(models.Video).filter(models.Video.id == request.video_id).first()
    if not video:
        raise HTTPException(status_code=44, detail="Video not found.")

    base, ext = os.path.splitext(video.filename)
    output_filename = f"{base}_text_overlay{ext}"
    output_path = os.path.join(EDIT_DIRECTORY, output_filename)

    # We tell FFmpeg to use our downloaded font file
    font_path = "NotoSansDevanagari-Regular.ttf"
    
    processed_file = video_processing.add_text_overlay(
        video.filepath, output_path, request.text, request.start_time, request.end_time, font_path=font_path
    )
    if not processed_file:
        raise HTTPException(status_code=500, detail="Failed to add text overlay.")

    return FileResponse(processed_file, media_type="video/mp4", filename=output_filename)

@router.post("/overlay/watermark", response_class=FileResponse)
async def add_watermark_api(
    request: WatermarkRequest, db: Session = Depends(models.get_db)
):
    video = db.query(models.Video).filter(models.Video.id == request.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")

    watermark_path = "logo.png" 
    if not os.path.exists(watermark_path):
        raise HTTPException(status_code=404, detail="Watermark file 'logo.png' not found in the 'backend' folder.")

    base, ext = os.path.splitext(video.filename)
    output_filename = f"{base}_watermarked{ext}"
    output_path = os.path.join(EDIT_DIRECTORY, output_filename)

    processed_file = video_processing.add_watermark(
        video.filepath, output_path, watermark_path
    )
    if not processed_file:
        raise HTTPException(status_code=500, detail="Failed to add watermark.")

    return FileResponse(processed_file, media_type="video/mp4", filename=output_filename)

@router.get("/download/{video_id}", response_class=FileResponse)
def download_video_quality(
    video_id: int,
    quality: str,
    db: Session = Depends(models.get_db)
):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
        
    if video.status != "complete":
        raise HTTPException(status_code=400, detail="Video is still processing. Please try again in a moment.")

    video_quality = db.query(models.VideoQuality).filter(
        models.VideoQuality.original_video_id == video_id,
        models.VideoQuality.quality == quality
    ).first()

    if not video_quality:
        raise HTTPException(status_code=404, detail=f"{quality} version not found for video ID {video_id}.")

    if not os.path.exists(video_quality.filepath):
        raise HTTPException(status_code=404, detail="File not found on server, processing may have failed.")

    return FileResponse(path=video_quality.filepath, media_type="video/mp4", filename=os.path.basename(video_quality.filepath))