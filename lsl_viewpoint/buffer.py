from __future__ import annotations  # post-poned evaluation of annotations

from typing import TYPE_CHECKING

import numpy as np

from .utils._checks import check_type, ensure_int

if TYPE_CHECKING:
    from typing import List, Tuple, Union

    from numpy.typing import NDArray


class Buffer:
    """Buffer holding the last samples.

    Parameters
    ----------
    ch_names : list of str | tuple of str
        Name of the channels.
    bufsize : int
        Number of samples to keep in the buffer, and pushed as one chunk to LSL.
    """

    def __init__(self, ch_names: Union[List[str], Tuple[str]], bufsize: int):
        check_type(ch_names, (list, tuple), "ch_names")
        for ch_name in ch_names:
            check_type(ch_name, (str,), "ch_name")
        bufsize = ensure_int(bufsize, "bufsize")
        self._buffer = np.zeros((bufsize, len(ch_names)))
        self._idx = 0

    def add_sample(self, data: NDArray[float]) -> None:
        """Add a sample to the buffer."""
        self._buffer[self._idx, :] = data
        self._idx += 1

    def reset(self) -> None:
        """Reset buffer increment."""
        self._idx = 0

    @property
    def buffer(self) -> NDArray[float]:
        """Buffer array."""
        return self._buffer

    @property
    def bufsize(self) -> int:
        """Number of samples in the buffer."""
        return self._buffer.shape[0]

    @property
    def n_channels(self) -> int:
        """Number of channels."""
        return self._buffer.shape[1]

    @property
    def is_full(self) -> bool:
        """True if the buffer is full."""
        return self._idx == self.bufsize
