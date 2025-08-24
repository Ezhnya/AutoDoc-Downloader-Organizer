
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    IMAP_HOST: str = os.getenv("IMAP_HOST", "imap.gmail.com")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    IMAP_USERNAME: str = os.getenv("IMAP_USERNAME", "")
    IMAP_PASSWORD: str = os.getenv("IMAP_PASSWORD", "")
    IMAP_MAILBOX: str = os.getenv("IMAP_MAILBOX", "INBOX")
    IMAP_SEARCH: str = os.getenv("IMAP_SEARCH", 'UNSEEN')

    BASE_DIR: Path = Path(os.getenv("BASE_DIR", str(Path.home() / "AutoDocs")))
    DOWNLOAD_DIR: Path = BASE_DIR / "downloads"
    ARCHIVE_DIR: Path = BASE_DIR / "archive"
    DB_PATH: Path = Path(os.getenv("DB_PATH", str(BASE_DIR / "autodoc.db")))

    ALLOWED_EXTENSIONS: tuple = tuple(os.getenv("ALLOWED_EXTENSIONS", ".pdf,.doc,.docx,.xls,.xlsx,.csv,.zip,.rar,.7z,.png,.jpg,.jpeg").split(","))
    MAX_EMAILS_PER_FETCH: int = int(os.getenv("MAX_EMAILS_PER_FETCH", "200"))
    MARK_SEEN: bool = os.getenv("MARK_SEEN", "true").lower() == "true"
    DELETE_AFTER_SAVE: bool = os.getenv("DELETE_AFTER_SAVE", "false").lower() == "false"

    LOCALE: str = os.getenv("LOCALE", "uk_UA")

def ensure_dirs(s: Settings):
    s.BASE_DIR.mkdir(parents=True, exist_ok=True)
    s.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    s.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    return s
