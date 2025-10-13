import os
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt

from PySide6.QtWidgets import QAbstractItemView

from .config import Settings, ensure_dirs
from . import db as dbmod
from .email_client import connect_imap, fetch_attachments
from .indexer import index_existing

class AutoDocApp(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.s = ensure_dirs(settings)
        self.setWindowTitle("AutoDoc Downloader & Organizer")
        self.resize(1100, 620)
        self.conn = dbmod.connect(self.s.DB_PATH)
        dbmod.init_db(self.conn)
        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Controls row
        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, sender, subject...")
        self.category_filter = QComboBox()
        self.category_filter.addItems(["", "documents", "spreadsheets", "invoices", "contracts", "reports", "tickets", "tax", "hr", "media", "archive", "uncategorized"])
        self.fetch_btn = QPushButton("Fetch from Email")
        self.index_btn = QPushButton("Reindex Folders")
        self.open_dir_btn = QPushButton("Open Archive Folder")

        controls.addWidget(QLabel("Category:"))
        controls.addWidget(self.category_filter, 1)
        controls.addWidget(self.search_input, 3)
        controls.addWidget(self.fetch_btn)
        controls.addWidget(self.index_btn)
        controls.addWidget(self.open_dir_btn)

        layout.addLayout(controls)

        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Sender", "Subject", "Received", "Saved", "Size (KB)"])
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table, 1)

        # Footer
        footer = QHBoxLayout()
        self.status = QLabel("Ready")
        self.open_btn = QPushButton("Open File")
        footer.addWidget(self.status, 1)
        footer.addWidget(self.open_btn)
        layout.addLayout(footer)

        # Signals
        self.fetch_btn.clicked.connect(self.on_fetch)
        self.index_btn.clicked.connect(self.on_index)
        self.open_dir_btn.clicked.connect(self.on_open_dir)
        self.open_btn.clicked.connect(self.on_open_file)
        self.search_input.textChanged.connect(self._refresh_table)
        self.category_filter.currentIndexChanged.connect(self._refresh_table)

    def _refresh_table(self):
        q = self.search_input.text().strip()
        cat = self.category_filter.currentText().strip()
        where = []
        params = []
        if q:
            where.append("(filename LIKE ? OR sender LIKE ? OR subject LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        if cat:
            where.append("category = ?")
            params.append(cat)
        where_clause = " AND ".join(where)
        rows = dbmod.query_documents(self.conn, where_clause, tuple(params))
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate(r):
                display_val = val
                if col == 8:
                    display_val = round((val or 0) / 1024, 1)
                item = QTableWidgetItem("" if display_val is None else str(display_val))
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, r[2])  # filepath hidden in id cell
                self.table.setItem(row, col, item)
        self.status.setText(f"Showing: {self.table.rowCount()} documents")

    def on_fetch(self):
        try:
            M = connect_imap(self.s.IMAP_HOST, self.s.IMAP_PORT, self.s.IMAP_USERNAME, self.s.IMAP_PASSWORD)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))
            return
        try:
            recs = fetch_attachments(
                M, self.s.IMAP_MAILBOX, self.s.IMAP_SEARCH, self.s.MAX_EMAILS_PER_FETCH,
                self.s.ALLOWED_EXTENSIONS, self.s.DOWNLOAD_DIR, self.s.ARCHIVE_DIR
            )
            count = 0
            for r in recs:
                try:
                    dbmod.insert_document(self.conn, r)
                    count += 1
                except Exception:
                    pass
            self.status.setText(f"Downloaded and saved: {count} files.")
            self._refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Fetch Error", str(e))
        finally:
            try:
                M.logout()
            except Exception:
                pass

    def on_index(self):
        count = 0
        for rec in index_existing(self.s.ARCHIVE_DIR):
            try:
                dbmod.insert_document(self.conn, rec)
                count += 1
            except Exception:
                pass
        self.status.setText(f"Reindexed: {count} files.")
        self._refresh_table()

    def on_open_dir(self):
        path = str(self.s.ARCHIVE_DIR)
        if os.name == "nt":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f"open '{path}'")
        else:
            os.system(f"xdg-open '{path}'")

    def on_open_file(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Open", "Select a document in the table.")
            return
        id_item = self.table.item(row, 0)
        filepath = id_item.data(Qt.ItemDataRole.UserRole)
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "File Not Found", "File path is invalid.")
            return
        if os.name == "nt":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            os.system(f"open '{filepath}'")
        else:
            os.system(f"xdg-open '{filepath}'")

def run_gui():
    app = QApplication(sys.argv)
    s = Settings()
    w = AutoDocApp(s)
    w.show()
    sys.exit(app.exec())
