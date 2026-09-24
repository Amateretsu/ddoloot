"""Resolved paths to the DDOLoot data directory and database files."""

import sys
from pathlib import Path

# When frozen by PyInstaller, _MEIPASS holds the extracted bundle root.
# In development the source layout is: src/ddoloot_ui/_paths.py → root is 3 up.
if getattr(sys, "frozen", False):
    _ROOT = Path(sys.executable).parent
else:
    _ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = _ROOT / "data"
LOOT_DB = DATA_DIR / "loot.db"
QUEUE_DB = DATA_DIR / "queue.db"
