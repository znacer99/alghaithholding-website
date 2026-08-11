#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
from datetime import datetime

DB_PATH = Path("instance/your_db.sqlite")
BACKUP_DIR = Path("instance/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

if DB_PATH.exists():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"your_db_{ts}.bak.sqlite"
    shutil.copy(DB_PATH, backup_file)
    print(f"✅ Backup created: {backup_file}")
else:
    print(f"⚠️ No database found at {DB_PATH}")
