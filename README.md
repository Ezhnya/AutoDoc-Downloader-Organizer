# AutoDoc Downloader & Organizer

Automatically fetches email attachments via IMAP, organizes them by category and month, and maintains a searchable SQLite database. User-friendly GUI built with PySide6 enables filtering, opening, and indexing documents efficiently.

## ✨ Key Features

* **IMAP Attachment Download**: Connect to your mailbox and fetch attachments automatically.
* **Smart Categorization**: Organize files by type and keywords (invoices, contracts, reports, media).
* **Automatic Folder Organization**: Archive structured by `category/YYYY-MM`.
* **SQLite Database**: Stores metadata including sender, subject, received date, file hash, and size.
* **Quick Search & Filters**: Find files by name, sender, subject, or category.
* **Reindex Existing Files**: Index files already placed in the archive.
* **One-Click File Opening**: Open files directly from the app.

## 🖥️ GUI Overview

* **Top Panel**: Category filter, search box, buttons for **Fetch from Mail**, **Reindex**, and **Open Archive Folder**.
* **Main Table**: Displays ID, filename, category, sender, subject, received date, saved date, and size.
* **Bottom Panel**: Status bar and **Open File** button.

## 🧩 Architecture

* `autodoc/config.py` – Configuration and `.env` loading.
* `autodoc/db.py` – SQLite database operations.
* `autodoc/email_client.py` – IMAP connection, email parsing, attachment saving, deduplication.
* `autodoc/classifier.py` – Categorizes files by keywords and extensions.
* `autodoc/organizer.py` – Determines storage paths `category/YYYY-MM/filename`.
* `autodoc/indexer.py` – Indexes existing archived files.
* `autodoc/gui.py` – PySide6 GUI with integrated search and actions.
* `main.py` – Entry point.

## 🚀 Quick Start

1. **Download** the repository or release.
2. **Create `.env`** file (see `.env.example`):

```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your_email@example.com
IMAP_PASSWORD=your_app_password
IMAP_MAILBOX=INBOX
IMAP_SEARCH=UNSEEN
# BASE_DIR=  # optional, defaults to ~/AutoDocs
```

> For Gmail, generate an **App Password** if 2FA is enabled.

3. **Install dependencies** (recommended via venv):

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

4. **Run the program**:

```bash
python main.py
```

5. Click **Fetch from Mail** to automatically save attachments in `BASE_DIR/archive/<category>/YYYY-MM/` and display metadata in the table.

## ⚙️ Configuration (`.env`)

* `IMAP_SEARCH`: e.g., `UNSEEN`, `ALL`, `FROM "billing@company.com"`, `SINCE 1-Aug-2025`.
* `ALLOWED_EXTENSIONS`: File types to download.
* `BASE_DIR`: Root folder for storage and database.
* `MAX_EMAILS_PER_FETCH`: Limit emails fetched at a time.

## 🔒 Security

* Passwords are only used during the IMAP session; never stored in the database.
* Use app passwords for Gmail or Exchange accounts.

## 🧠 Future Enhancements

* OCR / text search using Tesseract or PDFMiner.
* Automated routing based on sender.
* Export to Excel and notifications via Telegram bot.

👤 Author
Developed with by Ezhnya 🌐[GitHub](https://github.com/Ezhnya) |🤖[Telegram Channel](https://t.me/+2MllMZSL7EQyNDA6)

📜 License
This project is free for educational and personal use. Please credit the author: © 2025 Ezhnya

