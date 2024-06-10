"""Model for BIDS structure."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass(frozen=True)
class BidsModel:
    """Model of BIDS structure for generation, conversion and merging."""

    entities: List[BidsEntity]
    dataset_description: Dict[str, str]

    def _bids_subject_label(self, entity: BidsEntity) -> str:
        """Return BIDS subject label."""
        return f"sub-{entity.subject_id}"

    def _bids_task_label(self, entity: BidsEntity) -> str:
        """Return BIDS task label."""
        return f"task-{entity.task_name}"

    def _bids_session_label(self, entity: BidsEntity) -> Optional[str]:
        """Return BIDS session label."""
        return f"ses-{entity.session_id}" if entity.session_id else None

    def _bids_run_label(self, entity: BidsEntity) -> Optional[str]:
        """Return BIDS run label."""
        return f"run-{entity.run_id}" if entity.run_id else None

    @cached_property
    def has_sessions(self) -> bool:
        """Return True if BIDS model has sessions."""
        return any([entity.session_id for entity in self.entities])

    @cached_property
    def subject_ids(self) -> List[str]:
        """Return list of subject IDs."""
        return list(set([entity.subject_id for entity in self.entities]))


@dataclass(frozen=True)
class BidsEntity:
    """Model of BIDS entity, a representation of data within the BIDS structure.

    Entities can be files or tabular data.
    Only one of file or tabular_data should be set.
    """

    subject_id: str
    datatype: str
    task_name: str
    suffix: Optional[str] = field(default=None, repr=False)
    session_id: Optional[str] = field(default=None, repr=False)
    metadata: Optional[Dict[str, str]] = field(default=None, repr=False)
    file_path: Optional[Path] = field(default=None, repr=False)
    tabular_data: Optional[pd.DataFrame] = field(default=None, repr=False)
    run_id: Optional[str] = field(default=None, repr=False)

    def is_file_resource(self) -> bool:
        """Return True if entity is a file resource."""
        return self.file_path is not None

    def is_tabular_data(self) -> bool:
        """Return True if entity is tabular data."""
        return self.tabular_data is not None

    def extension(self) -> str:
        """Return extension of file resource."""
        return self.file_path.suffix if self.file_path is not None else ".tsv"

    @cached_property
    def attribute_dict(self) -> Dict[str, str]:
        """Construct a dict of all attributes for template filtering."""
        attributes = copy.deepcopy(self.metadata) if self.metadata is not None else {}
        attributes.update(
            {
                "subject_id": self.subject_id,
                "datatype": self.datatype,
                "task_name": self.task_name,
            }
        )
        if self.suffix:
            attributes["suffix"] = self.suffix
        if self.session_id:
            attributes["session_id"] = self.session_id
        if self.run_id:
            attributes["run_id"] = self.run_id
        return attributes


class BidsBuilder:
    """Builder for BIDS Model."""

    def __init__(self) -> None:
        """Initialize BIDS builder."""
        self._entities: list[BidsEntity] = []
        self._dataset_description: dict[str, Any] = {}

    def build(self) -> BidsModel:
        """Build BIDS model."""
        return BidsModel(self._entities, self._dataset_description)

    def add_dataset_description(
        self, name: str, bids_version: str, fields: Dict[str, Any]
    ) -> BidsBuilder:
        """Add dataset description.

        https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files.html#dataset_descriptionjson
        """
        self._dataset_description.update(
            {
                "Name": name,
                "BIDSVersion": bids_version,
            }
        )
        self._dataset_description.update(fields)
        return self

    def add(
        self,
        subject_id: str,
        datatype: str,
        task_name: str,
        resource: Path | pd.DataFrame,
        suffix: Optional[str] = None,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> BidsBuilder:
        """Add data to BIDS structure."""
        if isinstance(resource, Path):
            self._entities.append(
                BidsEntity(
                    subject_id=subject_id,
                    datatype=datatype,
                    task_name=task_name,
                    suffix=suffix,
                    session_id=session_id,
                    file_path=resource,
                    metadata=metadata,
                    run_id=run_id,
                )
            )
        elif isinstance(resource, pd.DataFrame):
            self._entities.append(
                BidsEntity(
                    subject_id=subject_id,
                    datatype=datatype,
                    task_name=task_name,
                    suffix=suffix,
                    session_id=session_id,
                    tabular_data=resource,
                    metadata=metadata,
                    run_id=run_id,
                )
            )
        else:
            raise ValueError("Resource must be a file path or tabular data.")
        return self
