from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # Make sure this is imported
from .routers import videos

app = FastAPI(
    title="Video Processing API",
    description="An API to upload, process, and manage videos.",
    version="1.0.0",
)

# This line makes the 'media' folder public
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(videos.router, prefix="/api", tags=["Videos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Processing API!"}