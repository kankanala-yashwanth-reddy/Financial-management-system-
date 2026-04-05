from __future__ import annotations

import importlib.util
from pathlib import Path

_path = Path(__file__).resolve().with_name("database-C.py")
_spec = importlib.util.spec_from_file_location("database_C", _path)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load database module from {_path}")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

for _name in dir(_mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_mod, _name)
