import os, shutil
from pathlib import Path
from .celery_app import celery
from ..services.storage import job_dir, make_output_path, presign_download, package_single_or_zip
from ..services import conversions

@celery.task(bind=True)
def convert_task(self, job_id: str, target: str, input_path: str | None = None, options: dict | None = None, multi_inputs: list[str] | None = None):
    options = options or {}
    jd = job_dir(job_id)
    src = Path(input_path) if input_path else None
    try:
        self.update_state(state="STARTED", meta={"progress": 5})

        if target == "mp4->mp3" and src:
            out = make_output_path(job_id, "mp3")
            bitrate = options.get("bitrate", "192k")
            conversions.mp4_to_mp3(src, out, bitrate=bitrate)
            final_path = out

        elif target == "pdf->jpg" and src:
            out_dir = jd / "images"
            dpi = int(options.get("dpi", 200))
            conversions.pdf_to_jpg(src, out_dir, dpi=dpi)
            imgs = sorted(out_dir.glob("page-*.jpg")) or sorted(out_dir.glob("page*.jpg")) or list(out_dir.glob("*.jpg"))
            final_path = package_single_or_zip(job_id, imgs, zip_name="pages")

        elif target == "jpg->pdf":
            dpi = int(options.get("dpi", 300))
            out = make_output_path(job_id, "pdf")
            if multi_inputs and len(multi_inputs) > 0:
                paths = [Path(p) for p in multi_inputs]
                conversions.images_to_pdf(paths, out, dpi=dpi)
            elif src:
                conversions.jpg_to_pdf(src, out, dpi=dpi)
            else:
                raise RuntimeError("No input files provided for jpg->pdf")
            final_path = out

        elif target == "docx->pdf" and src:
            conversions.docx_to_pdf(src, jd)
            pdfs = list(jd.glob("*.pdf"))
            if not pdfs:
                raise RuntimeError("No PDF produced by LibreOffice")
            final_path = package_single_or_zip(job_id, pdfs, zip_name="docs")

        else:
            raise ValueError(f"Unsupported target or missing input: {target}")

        download_url = presign_download(final_path)
        return {"progress": 100, "download_url": download_url}

    except Exception:
        raise
