from __future__ import annotations  # post-poned evaluation of annotations

import sys
from typing import TYPE_CHECKING

import pytest

from lsl_viewpoint import logger, set_log_level, load_config, write_config

if TYPE_CHECKING:
    from typing import Callable

logger.propagate = True
set_log_level("WARNING")


def requires_python39(function: Callable):
    """Check if we have python 3.9 or above."""
    if sys.version_info.major != 3:
        raise RuntimeError("This program is designed for python 3.")
    skip = sys.version_info.minor < 9
    reason = "Requires python 3.9 for 'importlib.resources.files'."
    return pytest.mark.skipif(skip, reason=reason)(function)


@requires_python39
def test_load_config():
    """Test configuration loader."""
    from importlib.resources import files

    cfg = files("lsl_viewpoint.tests") / "data" / "lsl-viewpoint-valid"
    path, sfreq = load_config(cfg)
    assert path == "/home/fcbg-hnp-meeg/VPX_InterApp_64.dll"
    assert sfreq == 60


@requires_python39
def test_write_config(tmp_path):
    """Test configuration writer."""
    from importlib.resources import files

    dll = files("lsl_viewpoint.tests") / "data" / "fake.dll"
    sfreq = 101
    fname = tmp_path / "config.ini"
    write_config(dll, sfreq, fname)
    dll_loaded, sfreq_loaded = load_config(fname)
    assert dll_loaded == str(dll)
    assert sfreq_loaded == sfreq


@pytest.mark.parametrize(
    "fname",
    ("lsl-viewpoint-invalid-1", "lsl-viewpoint-invalid-2", "lsl-viewpoint-invalid-3"),
)
@requires_python39
def test_load_invalid_config(caplog, fname):
    """Test loading of invalid configuration."""
    from importlib.resources import files

    cfg = files("lsl_viewpoint.tests") / "data" / fname
    caplog.clear()
    path, sfreq = load_config(cfg)
    assert "The configuration file is not correctly formatted." in caplog.text
    caplog.clear()
    assert path is None
    assert sfreq is None
