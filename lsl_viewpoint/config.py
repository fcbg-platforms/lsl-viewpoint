from __future__ import annotations  # post-poned evaluation of annotations

from typing import TYPE_CHECKING

from .utils._checks import ensure_path

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union


def load_config(fname: Union[str, Path]) -> Optional[str]:
    fname = ensure_path(fname, must_exist=False)
    if not fname.exists():
        return None


def write_config():
    pass
