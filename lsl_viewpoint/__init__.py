from ctypes import c_voidp, sizeof

from ._version import __version__  # noqa: F401
from .config import load_config, write_config
from .utils.config import sys_info  # noqa: F401
from .utils.logs import add_file_handler, logger, set_log_level  # noqa: F401

_LIB_PATH, _SAMPLING_RATE = load_config()

if not sizeof(c_voidp) == 8:
    raise RuntimeError("This package is for x64 windows system only.")


def set_config(path, sfreq):
    """Set the path to the ViewPoint library and the sampling rate."

    Parameters
    ----------
    path : path-like
        Path to the 'VPX_InterApp_64.dll' library to load.
    sfreq : float
        Sampling rate in Hz.
    """
    from ctypes import cdll

    from .utils._checks import check_type, ensure_path

    check_type(sfreq, ("numeric",), "sfreq")
    path = ensure_path(path, must_exist=True)
    if path.name != "VPX_InterApp_64.dll":
        logger.warning(
            "The expected name of the DLL is 'VPX_InterApp_64.dll' corresponding to "
            "the x64 architecture. The provided DLL '%s' might or might not work.",
            path.name,
        )
    path = str(path)
    try:
        cdll.LoadLibrary(path)
    except Exception:
        raise RuntimeError(
            "The DLL could not be loaded. Please check the version and the "
            "dependencies."
        )

    global _LIB_PATH
    _LIB_PATH = path
    global _SAMPLING_RATE
    _SAMPLING_RATE = float(sfreq)
    write_config(_LIB_PATH, _SAMPLING_RATE)
