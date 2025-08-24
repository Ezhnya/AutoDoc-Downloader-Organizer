
import email
import imaplib
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from .classifier import guess_category
from .organizer import build_target_path

def _decode_header(value: str) -> str:
    from email.header import decode_header, make_header
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value

def connect_imap(host: str, port: int, username: str, password: str) -> imaplib.IMAP4_SSL:
    M = imaplib.IMAP4_SSL(host, port)
    M.login(username, password)
    return M

def fetch_attachments(
    M: imaplib.IMAP4_SSL,
    mailbox: str,
    search: str,
    max_emails: int,
    allowed_ext: tuple,
    download_dir: Path,
    archive_dir: Path
) -> List[Dict[str, Any]]:
    results = []
    typ, _ = M.select(mailbox)
    if typ != "OK":
        raise RuntimeError(f"Cannot select mailbox {mailbox}")
    typ, data = M.search(None, *search.split())
    if typ != "OK":
        return results
    ids = data[0].split()
    if max_emails and len(ids) > max_emails:
        ids = ids[-max_emails:]
    for i in ids:
        typ, msg_data = M.fetch(i, "(RFC822)")
        if typ != "OK":
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        sender = _decode_header(msg.get("From", ""))
        subject = _decode_header(msg.get("Subject", ""))
        date_raw = msg.get("Date")
        try:
            received_at = email.utils.parsedate_to_datetime(date_raw).isoformat()
        except Exception:
            received_at = datetime.utcnow().isoformat()

        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            filename = part.get_filename()
            if not filename:
                continue
            filename = _decode_header(filename)
            ext = os.path.splitext(filename)[1].lower()
            if allowed_ext and ext not in allowed_ext:
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            h = hashlib.sha256(payload).hexdigest()
            category = guess_category(filename, subject, sender)
            download_dir.mkdir(parents=True, exist_ok=True)
            tmp_path = download_dir / filename
            base, ext = os.path.splitext(filename)
            counter = 1
            while tmp_path.exists():
                tmp_path = download_dir / f"{base}_{counter}{ext}"
                counter += 1
            with open(tmp_path, "wb") as f:
                f.write(payload)
            size_bytes = tmp_path.stat().st_size
            final_path = build_target_path(archive_dir, category, received_at, tmp_path.name)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(tmp_path, final_path)
            results.append({
                "filename": final_path.name,
                "filepath": str(final_path),
                "category": category,
                "sender": sender,
                "subject": subject,
                "received_at": received_at,
                "size_bytes": size_bytes,
                "hash_sha256": h,
            })
    return results
