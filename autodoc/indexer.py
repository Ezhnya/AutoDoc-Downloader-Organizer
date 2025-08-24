
from pathlib import Path
import hashlib
from datetime import datetime

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def index_existing(base_dir: Path):
    for p in base_dir.rglob("*"):
        if not p.is_file():
            continue
        try:
            stat = p.stat()
            yield {
                "filename": p.name,
                "filepath": str(p),
                "category": p.parent.parent.name if p.parent.parent != base_dir else "unknown",
                "sender": None,
                "subject": None,
                "received_at": datetime.utcfromtimestamp(stat.st_mtime).isoformat(),
                "size_bytes": stat.st_size,
                "hash_sha256": file_sha256(p),
            }
        except Exception:
            continue
