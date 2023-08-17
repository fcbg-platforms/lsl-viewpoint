from ctypes import CDLL, c_voidp, cdll, sizeof
from importlib.resources import files
from typing import TYPE_CHECKING

from .utils._checks import ensure_path
from .utils.logs import logger

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union


def load_lib(path: Optional[Union[str, Path]] = None):
    """Load the ViewPoint DLL.

    Parameters
    ----------
    path : path-like | None
        Path to the VPX_InterApp_64.dll to load.

    Returns
    -------
    vpx : CDLL
        The loaded library.
    """
    if not sizeof(c_voidp) == 8:
        raise RuntimeError("This package is for x64 system only.")
    if path is None:
        path = files("lsl_viewpoint") / "lib" / "VPX_InterApp_64.dll"
    else:
        path = ensure_path(path, must_exist=True)
    if path.name != "VPX_InterApp_64.dll":
        logger.warning(
            "The expected name of the DLL is 'VPX_InterApp_64.dll' corresponding to "
            "the x64 architecture. The provided DLL %s might or might not work.",
            path.name,
        )
    try:
        cdll.LoadLibrary(path)
        vpx = CDLL(path)
    except Exception:
        raise RuntimeError(
            "The DLL could not be loaded. Please check the version and the "
            "dependencies."
        )
    return vpx
