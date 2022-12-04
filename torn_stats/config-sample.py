from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.resolve() / "data"

CACHE_TYPE = "FileSystemCache"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DEFAULT_TIMEOUT = 300

DEBUG = False

TORN_API_KEY = ""
