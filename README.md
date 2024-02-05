[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![tests](https://github.com/fcbg-hnp-meeg/lsl-viewpoint/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/fcbg-hnp-meeg/lsl-viewpoint/actions/workflows/pytest.yml)

# LSL ViewPoint

LSL application for the viewpoint eye-tracker system.
Designed for x64 bits windows systems only.

## Installation

This LSL application is a python package. It can be installed with `pip` from source:

```
pip install git+https://github.com/fcbg-hnp-meeg/lsl-viewpoint
```

## Configuration

This LSL application requires 2 configuration variables: the path to
`VPX_InterApp_64.dll` and the set sampling rate. The `VPX_InterApp_64.dll` should be the
one in use by the ViewPoint application. Both configuration variables can be set with
`lsl_viewpoint.set_config`:

```
from lsl_viewpoint import set_config

path = "C:/Applications/Arrington/VPX_InterApp_64.dll"
sfreq = 60
set_config(path, sfreq)
```

The configuration variables are saved in a file `~/.lsl-viewpoint`.

## Streaming data to LSL

The stream of data starts as soon as the module `lsl_viewpoint.callback` is imported.
Thus `from lsl_viewpoint.callback import VPX` will start the streaming. It is not
recommended to ever import the `callback` module. Instead, the entry-point
`lsl_viewpoint` should be called in a terminal:

```
lsl_viewpoint --help
```
