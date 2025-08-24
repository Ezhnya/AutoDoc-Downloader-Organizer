
import re
from pathlib import Path
from typing import Optional

KEYWORDS = {
    "invoices": ["invoice", "рахунок", "счет", "оплата", "bill"],
    "contracts": ["contract", "договір", "договор", "agreement"],
    "reports": ["report", "звіт", "отчет", "statement"],
    "tickets": ["ticket", "квиток", "билет", "boarding"],
    "tax": ["tax", "подат", "налог", "vat"],
    "hr": ["resume", "cv", "відгук", "відпуст", "кадри", "hr"],
    "media": ["image", "photo", "png", "jpg", "jpeg", "screenshot"],
    "archive": ["zip", "rar", "7z", "archive"],
}

EXTENSION_MAP = {
    ".pdf": "documents",
    ".doc": "documents",
    ".docx": "documents",
    ".xls": "spreadsheets",
    ".xlsx": "spreadsheets",
    ".csv": "spreadsheets",
    ".png": "media",
    ".jpg": "media",
    ".jpeg": "media",
    ".zip": "archive",
    ".rar": "archive",
    ".7z": "archive",
}

def guess_category(filename: str, subject: Optional[str] = None, sender: Optional[str] = None) -> str:
    name = filename.lower()
    cat = EXTENSION_MAP.get(Path(filename).suffix.lower())
    if cat:
        return cat
    text = " ".join([name, subject or "", sender or ""]).lower()
    for category, words in KEYWORDS.items():
        for w in words:
            if re.search(r"\b" + re.escape(w) + r"\b", text):
                return category
    return "uncategorized"
