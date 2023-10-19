import os
from pathlib import Path

CONFIG_DIR = Path(os.path.dirname(__file__))

ROOT_DIR = CONFIG_DIR.parent

LOG_DIR = os.path.join(ROOT_DIR,'log')