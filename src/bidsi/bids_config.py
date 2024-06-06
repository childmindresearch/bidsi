"""Config object for Bidsi."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class MergeStrategy(Enum):
    """Merge strategy for BIDS structure.

    NO_MERGE: Do not merge, exit with error on conflict.
    OVERWRITE: Overwrite existing files on conflict.
    KEEP: Keep existing files on conflict.
    RENAME_SEQUENTIAL: Rename files on conflict using run-label increments.
    """

    # Do not merge, only proceed with empty BIDS root.
    # Exit with error on conflict. Default.
    NO_MERGE = "NO_MERGE"

    # Overwrite existing files on conflict.
    OVERWRITE = "OVERWRITE"

    # Keep existing files on conflict.
    KEEP = "KEEP"

    # Rename files on conflict using run-label increments.
    RENAME_SEQUENTIAL = "RENAME_SEQUENTIAL"

    # Merge directories, JSON metadata or tabular data. Error on other types.
    MERGE = "MERGE"

    def __str__(self) -> str:
        """Return string representation of MergeStrategy."""
        return self.name

    def __repr__(self) -> str:
        """Return string representation of MergeStrategy."""
        return f"{self.__class__}.{str(self)}"

    @staticmethod
    def argparse(s: str) -> MergeStrategy:
        """Parse MergeStrategy from argparse string."""
        return MergeStrategy[s.upper()]


@dataclass
class BidsStructureConfig:
    """Structure config."""

    clean_fields: bool = True
    include_session_dir: bool = False


@dataclass
class BidsMergeConfig:
    """Merge config."""

    participants: MergeStrategy = field(default=MergeStrategy.MERGE)
    dataset_description: MergeStrategy = field(default=MergeStrategy.MERGE)
    entity_metadata: MergeStrategy = field(default=MergeStrategy.MERGE)
    entity: MergeStrategy = field(default=MergeStrategy.OVERWRITE)
    subject_dir: MergeStrategy = field(default=MergeStrategy.MERGE)
    session_dir: MergeStrategy = field(default=MergeStrategy.RENAME_SEQUENTIAL)


@dataclass
class EntityTemplateFilter:
    """Entity naming template filter."""

    field: str
    pattern: str


@dataclass
class EntityTemplate:
    """Entity naming template."""

    name: str
    suffix: str
    fields: list[str] = field(default_factory=list)
    filters: list[EntityTemplateFilter] = field(default_factory=list)


@dataclass
class EntityConfig:
    """Config for entity naming."""

    templates: list[EntityTemplate] = field(default_factory=list)
    default_template: list[str] = field(
        default_factory=lambda: ["subject", "task", "suffix"]
    )


# @dataclass
class BidsConfig(BaseSettings):
    """Config object for Bidsi."""

    model_config = SettingsConfigDict(revalidate_instances="always")

    structure: BidsStructureConfig = BidsStructureConfig()
    merge: BidsMergeConfig = BidsMergeConfig()
    entity: EntityConfig = EntityConfig()

    @classmethod
    def from_file(cls, config_file: Path) -> BidsConfig:
        """Create BidsConfig object from file."""
        with config_file.open("rb") as file:
            return cls.from_dict(tomllib.load(file))

    @classmethod
    def from_string(cls, config_string: str) -> BidsConfig:
        """Create BidsConfig object from string."""
        return cls.from_dict(tomllib.loads(config_string))

    @classmethod
    def from_dict(cls, config_dict: dict) -> BidsConfig:
        """Create BidsConfig object from dictionary."""
        # return from_dict(data_class=cls, data=config_dict, config=Config(cast=[Enum]))
        return cls.model_validate(config_dict)
