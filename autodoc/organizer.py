
from pathlib import Path
from datetime import datetime

def build_target_path(base_dir: Path, category: str, received_at: str, filename: str) -> Path:
    try:
        dt = datetime.fromisoformat(received_at.replace("Z",""))
    except Exception:
        dt = datetime.now()
    sub = f"{dt.year}-{dt.month:02d}"
    target_dir = base_dir / category / sub
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename
