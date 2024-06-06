"""BIDS Structure Generation Library."""

from .bids_config import BidsConfig, MergeStrategy
from .bids_conversion import Bidsifiable
from .bids_model import BidsBuilder, BidsEntity, BidsModel
from .bids_writer import BidsWriter

__all__ = [
    "BidsWriter",
    "MergeStrategy",
    "BidsBuilder",
    "BidsConfig",
    "BidsEntity",
    "BidsModel",
    "Bidsifiable",
]
