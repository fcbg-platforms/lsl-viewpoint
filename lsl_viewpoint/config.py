from __future__ import annotations  # post-poned evaluation of annotations

from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING

from .utils._checks import check_type, ensure_path
from .utils.logs import logger

if TYPE_CHECKING:
    from typing import Optional, Tuple, Union


def load_config(
    fname: Union[str, Path] = Path.home() / ".lsl-viewpoint"
) -> Tuple[Optional[str], Optional[float]]:
    """Load a configuration file with the path to 'VPX_InterApp_64.dll'."""
    fname = ensure_path(fname, must_exist=False)
    if not fname.exists():
        return None, None
    config = ConfigParser(inline_comment_prefixes=("#", ";"))
    config.optionxform = str
    config.read(fname)
    try:
        lib_path = config["config"]["VPX_InterApp_64.dll"]
        sfreq = float(config["config"]["sfreq"])
    except Exception:
        logger.warning("The configuration file is not correctly formatted.")
        lib_path = None
        sfreq = None
    return lib_path, sfreq


def write_config(
    path: Union[str, Path],
    sfreq: float,
    fname: Union[str, Path] = Path.home() / ".lsl-viewpoint",
) -> None:
    """Write a configuration file with the path to 'VPX_InterApp_64.dll'."""
    path = ensure_path(path, must_exist=True)
    check_type(sfreq, ("numeric",), "sfreq")
    fname = ensure_path(fname, must_exist=False)
    config = ConfigParser(inline_comment_prefixes=("#", ";"))
    config.optionxform = str
    config["config"] = {"VPX_InterApp_64.dll": str(path), "sfreq": sfreq}
    with open(fname, "w") as cfg:
        config.write(cfg)
