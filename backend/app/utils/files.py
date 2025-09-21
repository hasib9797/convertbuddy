import re, unicodedata
from pathlib import Path

def safe_filename(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('._')
    return name or 'file'
