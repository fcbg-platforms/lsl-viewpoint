"""Backport of features unavailable in BSL 0.6.1."""

from __future__ import annotations  # c.f. PEP 563, PEP 649

from typing import TYPE_CHECKING

from bsl.lsl import StreamInfo as StreamInfoBSL

from .utils._checks import check_type
from .utils._docs import copy_doc
from .utils.logs import logger

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union

_MAPPING_LSL = {
    "ch_names": "label",
    "ch_types": "type",
    "ch_units": "unit",
}


@copy_doc(StreamInfoBSL)
class StreamInfo(StreamInfoBSL):
    def get_channel_names(self) -> Optional[List[str]]:
        """Get the channel names in the description.

        Returns
        -------
        ch_names : list of str or ``None`` | None
            List of channel names, matching the number of total channels.
            If ``None``, the channel names are not set.

            .. warning::

                If a list of str and ``None`` are returned, some of the channel names
                are missing. This is not expected and could occur if the XML tree in
                the ``desc`` property is tempered with outside of the defined getter and
                setter.
        """
        return self._get_channel_info("ch_names")

    def get_channel_types(self) -> Optional[List[str]]:
        """Get the channel types in the description.

        Returns
        -------
        ch_types : list of str or ``None`` | None
            List of channel names, matching the number of total channels.
            If ``None``, the channel types are not set.

            .. warning::

                If a list of str and ``None`` are returned, some of the channel types
                are missing. This is not expected and could occur if the XML tree in
                the ``desc`` property is tempered with outside of the defined getter and
                setter.
        """
        return self._get_channel_info("ch_types")

    def get_channel_units(self) -> Optional[List[str]]:
        """Get the channel units in the description.

        Returns
        -------
        ch_units : list of str or ``None`` | None
            List of channel units, matching the number of total channels.
            If ``None``, the channel units are not set.

            .. warning::

                If a list of str and ``None`` are returned, some of the channel units
                are missing. This is not expected and could occur if the XML tree in
                the ``desc`` property is tempered with outside of the defined getter and
                setter.
        """
        return self._get_channel_info("ch_units")

    def _get_channel_info(self, name: str) -> Optional[List[str]]:
        """Get the 'channel/name' element in the XML tree."""
        if self.desc.child("channels").empty():
            return None

        channels = self.desc.child("channels")
        ch_infos = list()
        ch = channels.child("channel")
        while not ch.empty():
            ch_info = ch.child(_MAPPING_LSL[name]).first_child().value()
            if len(ch_info) != 0:
                ch_infos.append(ch_info)
            else:
                ch_infos.append(None)
            ch = ch.next_sibling()

        if all(ch_info is None for ch_info in ch_infos):
            return None
        if len(ch_infos) != self.n_channels:
            logger.warning(
                "The stream description contains %i elements for %i channels.",
                len(ch_infos),
                self.n_channels,
            )
        return ch_infos

    def set_channel_names(self, ch_names: Union[List[str], Tuple[str]]) -> None:
        """Set the channel names in the description. Existing labels are overwritten.

        Parameters
        ----------
        ch_names : sequence of str
            List of channel names, matching the number of total channels.
        """
        self._set_channel_info(ch_names, "ch_names")

    def set_channel_types(self, ch_types: Union[str, List[str]]) -> None:
        """Set the channel types in the description. Existing types are overwritten.

        The types are given as human readable strings, e.g. ``'eeg'``.

        Parameters
        ----------
        ch_types : sequence of str | str
            List of channel types, matching the number of total channels.
            If a single `str` is provided, the type is applied to all channels.
        """
        ch_types = (
            [ch_types] * self.n_channels if isinstance(ch_types, str) else ch_types
        )
        self._set_channel_info(ch_types, "ch_types")

    def set_channel_units(self, ch_units: Union[str, List[str]]) -> None:
        """Set the channel units in the description. Existing units are overwritten.

        The units are given as human readable strings, e.g. ``'microvolts'``.

        Parameters
        ----------
        ch_units : sequence of str | str
            List of channel units, matching the number of total channels.
            If a single `str` is provided, the unit is applied to all channels.

        Notes
        -----
        Some channel types do not have a unit. The `str` ``none`` should be used to
        denote a this channel unit, corresponding to ``FIFF_UNITM_NONE`` in MNE.
        """
        ch_units = (
            [ch_units] * self.n_channels if isinstance(ch_units, str) else ch_units
        )
        self._set_channel_info(ch_units, "ch_units")

    def _set_channel_info(self, ch_infos: List[str], name: str) -> None:
        """Set the 'channel/name' element in the XML tree."""
        check_type(ch_infos, (list, tuple), name)
        for ch_info in ch_infos:
            check_type(ch_info, (str,), name.rstrip("s"))
        if len(ch_infos) != self.n_channels:
            raise ValueError(
                f"The number of provided channel {name.lstrip('ch_')} {len(ch_infos)} "
                f"must match the number of channels {self.n_channels}."
            )

        if self.desc.child("channels").empty():
            channels = self.desc.append_child("channels")
        else:
            channels = self.desc.child("channels")

        # fill the 'channel/name' element of the tree and overwrite existing values
        ch = channels.child("channel")
        for ch_info in ch_infos:
            if ch.empty():
                ch = channels.append_child("channel")

            if ch.child(_MAPPING_LSL[name]).empty():
                ch.append_child_value(_MAPPING_LSL[name], ch_info)
            else:
                ch.child(_MAPPING_LSL[name]).first_child().set_value(ch_info)
            ch = ch.next_sibling()

        # in case the original sinfo was tempered with and had more 'channel' than the
        # correct number of channels
        while not ch.empty():
            ch_next = ch.next_sibling()
            channels.remove_child(ch)
            ch = ch_next
