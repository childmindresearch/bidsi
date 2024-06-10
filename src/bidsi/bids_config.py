"""Config object for Bidsi."""

from __future__ import annotations

import logging
import re
import tomllib
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from .bids_model import BidsEntity

LOG = logging.getLogger(__name__)


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

    include_session_dir: bool = False


@dataclass
class BidsMergeConfig:
    """Merge config."""

    # Merge strategy for BIDS structure. Whether to merge BIDS root. Default: NO_MERGE.
    bids: MergeStrategy = field(default=MergeStrategy.NO_MERGE)

    # Merge strategy for participants.tsv. Default: MERGE.
    participants: MergeStrategy = field(default=MergeStrategy.MERGE)

    # Merge strategy for dataset_description.json. Default: MERGE.
    dataset_description: MergeStrategy = field(default=MergeStrategy.MERGE)

    # Merge strategy for entity metadata as JSON sidecar. Default: MERGE.
    entity_metadata: MergeStrategy = field(default=MergeStrategy.MERGE)

    # Merge strategy for entity files. Default: OVERWRITE.
    entity: MergeStrategy = field(default=MergeStrategy.OVERWRITE)

    # Merge strategy for subject directories. Default: MERGE.
    subject_dir: MergeStrategy = field(default=MergeStrategy.MERGE)

    # Merge strategy for session directories. Default: RENAME_SEQUENTIAL.
    session_dir: MergeStrategy = field(default=MergeStrategy.RENAME_SEQUENTIAL)


@dataclass
class EntityTemplateFilter:
    """Entity naming template filter."""

    field: str
    pattern: str

    def match(self, entity: BidsEntity) -> bool:
        """Match entity against filter."""
        return (
            self.field in entity.attribute_dict()
            and re.match(self.pattern, entity.attribute_dict()[self.field]) is not None
        )


@dataclass
class EntityTemplate:
    """Entity naming template."""

    # Name of template, used for logging only.
    name: str

    # Override suffix for entity name. If None, uses suffix defined in BidsEntity.
    # Should not include file extension, which is computed in BidsEntity based on
    # original file/data type.
    suffix: Optional[str] = None

    # List of fields to include in entity name, in order.
    # Should match fields in BidsEntity or keys in BidsEntity.metadata.
    # Will be subsituted with abbreviations if present in abbreviations dictionary.
    template: list[str] = field(default_factory=list)

    # List of filters to apply to entity before naming.
    filters: list[EntityTemplateFilter] = field(default_factory=list)

    def match(self, entity: BidsEntity) -> bool:
        """Match entity against template."""
        # Check if all filters match.
        return all(filter_.match(entity) for filter_ in self.filters)

    def maybe_clean(self, field: str, clean: bool) -> str:
        """Maybe clean BIDS field value."""
        return re.sub(r"[^a-zA-Z0-9]", "", field) if clean else field

    def entity_name(
        self, entity: BidsEntity, clean: bool = True, abbrev: dict[str, str] = {}
    ) -> str:
        """Generate entity name from entity."""
        entity_dict = entity.attribute_dict()
        name_pieces = []
        # Iterate over template.
        for template_field in self.template:
            if template_field not in entity_dict:
                raise ValueError(
                    f"Template field {template_field} not in entity {entity}"
                )
            if template_field in abbrev:
                name_pieces.append(
                    f"{self.maybe_clean(abbrev[template_field], clean)}-"
                    f"{self.maybe_clean(entity_dict[template_field], clean)}"
                )
            else:
                name_pieces.append(
                    f"{self.maybe_clean(template_field, clean)}-"
                    f"{self.maybe_clean(entity_dict[template_field], clean)}"
                )
        # Use override suffix if present, otherwise use entity suffix.
        # Exclude if neither is present.
        entity_suffix = self.suffix if self.suffix is not None else entity.suffix
        if entity_suffix is None or entity_suffix == "":
            LOG.info(
                f"No suffix for entity {entity}: "
                f"skipping suffix in template ({self.name})."
            )
        else:
            name_pieces.append(self.maybe_clean(entity_suffix, clean))

        # Add '.' to extension if not present.
        entity_filename = "_".join(name_pieces) + entity.extension()
        LOG.debug(
            f"Entity name for {entity} using template {self.name}: {entity_filename}"
        )

        return entity_filename


@dataclass
class EntityConfig:
    """Config for entity naming."""

    templates: list[EntityTemplate] = field(default_factory=list)
    default_template: EntityTemplate = field(
        default_factory=lambda: EntityTemplate(
            name="default", suffix="", template=["subject_id", "task_name"], filters=[]
        )
    )
    clean_fields: bool = True
    supplemental_abbreviations: dict[str, str] = field(default_factory=dict)

    @cached_property
    def abbreviations(self) -> dict[str, str]:
        """Return combined standard and supplemental abbreviations."""
        standard_abbreviations = {
            "subject_id": "sub",
            "task_name": "task",
            "session_id": "ses",
            "run_id": "run",
        }
        return {**standard_abbreviations, **self.supplemental_abbreviations}

    def entity_name(self, entity: BidsEntity) -> str:
        """Generate entity name from entity."""
        # Iterate over templates.
        for template in self.templates:
            if template.match(entity):
                return template.entity_name(
                    entity, self.clean_fields, self.abbreviations
                )
        return self.default_template.entity_name(
            entity, self.clean_fields, self.abbreviations
        )

    def entity_metadata_name(self, entity: BidsEntity) -> str:
        """Generate entity metadata name from entity."""
        return str(Path(self.entity_name(entity)).with_suffix(".json"))


class BidsConfig(BaseSettings):
    """Config object for Bidsi."""

    model_config = SettingsConfigDict(revalidate_instances="always")

    structure: BidsStructureConfig = BidsStructureConfig()
    merge: BidsMergeConfig = BidsMergeConfig()
    entity: EntityConfig = EntityConfig()

    @classmethod
    def default(cls) -> BidsConfig:
        """Return default BIDS configuration."""
        return BidsConfig()

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
        return cls.model_validate(config_dict)
