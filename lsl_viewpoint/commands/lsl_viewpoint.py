import argparse

from .. import set_log_level


def run():
    """Run lsl_viewpoint() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}",
        description="Streams ViewPoint Data on LSL.",
    )
    parser.add_argument("--verbose", help="enable debug logs", action="store_true")
    args = parser.parse_args()

    set_log_level("DEBUG" if args.verbose else "INFO")

    # the import starts the callback loop
    from ..callback import VPX  # noqa: F401
