from __future__ import annotations  # post-poned evaluation of annotations

from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING

from .utils._checks import ensure_path
from .utils._logs import logger

if TYPE_CHECKING:
    from typing import Optional, Union


def load_config(
    fname: Union[str, Path] = Path.home() / ".lsl-viewpoint"
) -> Optional[str]:
    """Load a configuration file with the path to 'VPX_InterApp_64.dll'."""
    fname = ensure_path(fname, must_exist=False)
    if not fname.exists():
        return None
    config = ConfigParser(inline_comment_prefixes=("#", ";"))
    config.optionxform = str
    config.read(fname)
    try:
        lib_path = config["path"]["VPX_InterApp_64.dll"]
    except Exception:
        logger.warning("The configuration file is not correctly formatted.")
        lib_path = None
    return lib_path


def write_config(
    path: Union[str, Path], fname: Union[str, Path] = Path.home() / ".lsl-viewpoint"
) -> None:
    """Write a configuration file with the path to 'VPX_InterApp_64.dll'."""
    path = ensure_path(path, must_exist=True)
    fname = ensure_path(fname, must_exist=False)
    config = ConfigParser(inline_comment_prefixes=("#", ";"))
    config.optionxform = str
    config["path"] = {"VPX_InterApp_64.dll": str(path)}
    with open(fname, "w") as cfg:
        config.write(cfg)
