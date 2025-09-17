import ffmpeg
import os

def get_video_metadata(filepath: str):
    """Gets duration and size of a video file."""
    try:
        probe = ffmpeg.probe(filepath)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        duration = float(probe['format']['duration'])
        size = int(probe['format']['size'])
        return {"duration": duration, "size": size}
    except ffmpeg.Error as e:
        print(f"Error probing video: {e.stderr}")
        return None

def trim_video(input_path: str, output_path: str, start: float, end: float):
    """Trims a video using ffmpeg."""
    try:
        (
            ffmpeg
            .input(input_path, ss=start)
            .output(output_path, to=end-start, c='copy')
            .run(overwrite_output=True, quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"Error trimming video: {e.stderr}")
        return None

def add_text_overlay(input_path: str, output_path: str, text: str, start: int, end: int, font_path: str = None):
    """Adds a text overlay to a video."""
    # This part adds the font file to the command if one is provided
    font_file_cmd = f":fontfile={font_path}" if font_path else ""
    
    drawtext_filter = f"drawtext=text='{text}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=60:fontcolor=white:enable='between(t,{start},{end})'{font_file_cmd}"
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vf=drawtext_filter)
            .run(overwrite_output=True, quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"Error adding text overlay: {e.stderr}")
        return None

def add_watermark(input_path: str, output_path: str, watermark_path: str):
    """Adds an image watermark to the bottom-right corner of a video."""
    main_video = ffmpeg.input(input_path)
    watermark = ffmpeg.input(watermark_path)
    try:
        (
            ffmpeg
            # This complex filter resizes the watermark to 1/10th of the video width
            # and then places it in the bottom-right corner.
            .filter_complex(
                '[1:v]scale=iw/10:-1[wm];[0:v][wm]overlay=W-w-10:H-h-10'
            )
            .output(output_path)
            .run(overwrite_output=True, quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"Error adding watermark: {e.stderr}")
        return None

def transcode_video(input_path: str, output_path: str, quality: str):
    """Transcodes a video to a specific quality (e.g., '720p')."""
    heights = {"1080p": 1080, "720p": 720, "480p": 480}
    if quality not in heights:
        return None
    height = heights[quality]
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, vf=f'scale=-2:{height}', preset='fast', vcodec='libx264')
            .run(overwrite_output=True, quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"Error transcoding video: {e.stderr}")
        return None