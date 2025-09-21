from pathlib import Path
import subprocess

class ConversionError(Exception):
    pass

def run(args: list[str]):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ConversionError(proc.stderr.strip() or f"Command failed: {' '.join(args)}")
    return proc.stdout.strip()

def mp4_to_mp3(src: Path, dst: Path, bitrate: str = "192k"):
    run([
        "ffmpeg", "-y",
        "-i", str(src),
        "-vn",
        "-ab", str(bitrate),
        str(dst),
    ])

def pdf_to_jpg(src: Path, dst_dir: Path, dpi: int = 200):
    dst_dir.mkdir(parents=True, exist_ok=True)
    # Produces files like page-1.jpg, page-2.jpg
    run([
        "pdftoppm",
        "-jpeg",
        "-r", str(dpi),
        str(src),
        str(dst_dir / "page")
    ])

def jpg_to_pdf(src: Path, dst: Path, dpi: int = 300):
    run([
        "magick",
        str(src),
        "-units", "PixelsPerInch",
        "-density", str(dpi),
        str(dst),
    ])

def docx_to_pdf(src: Path, out_dir: Path):
    run([
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(src),
    ])
