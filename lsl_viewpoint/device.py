from ctypes import Structure, c_float
from typing import TYPE_CHECKING

from . import load_lib
from .constants import VPX_STATUS_ViewPointIsRunning

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union


class RealPoint(Structure):
    _fields_ = [("x", c_float), ("y", c_float)]


class ViewPointDevice:
    def __init__(self, path: Optional[Union[str, Path]] = None) -> None:
        self._vpx = load_lib(path)
        if self._vpx.VPX_GetStatus(VPX_STATUS_ViewPointIsRunning) < 1:
            raise RuntimeError("ViewPoint is not running.")

    def send_command(self, command: str):
        return self._vpx.VPX_SendCommandString(str(command).encode("ascii"))
