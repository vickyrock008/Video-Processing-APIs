from sqlalchemy import (Column, Integer, String, Float, DateTime, ForeignKey,
                        create_engine)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Database URL from your alembic.ini - make sure they match!
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:2003@localhost/video"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Database Table Models ---

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String, unique=True)
    duration = Column(Float)
    size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.utcnow)
    # --- THIS IS THE NEW LINE ---
    status = Column(String, default="processing") # Add this status field

    # Relationships
    trims = relationship("TrimmedVideo", back_populates="original_video")
    qualities = relationship("VideoQuality", back_populates="original_video")

class TrimmedVideo(Base):
    __tablename__ = 'trimmed_videos'
    id = Column(Integer, primary_key=True, index=True)
    original_video_id = Column(Integer, ForeignKey('videos.id'))
    filepath = Column(String, unique=True)
    start_time = Column(Float)
    end_time = Column(Float)

    original_video = relationship("Video", back_populates="trims")

class VideoQuality(Base):
    __tablename__ = 'video_qualities'
    id = Column(Integer, primary_key=True, index=True)
    original_video_id = Column(Integer, ForeignKey('videos.id'))
    filepath = Column(String, unique=True)
    quality = Column(String) # e.g., "1080p", "720p"

    original_video = relationship("Video", back_populates="qualities")