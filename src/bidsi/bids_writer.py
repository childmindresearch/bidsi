"""Writer for BIDS Model."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, Optional, Type

import pandas as pd

from bidsi.bids_config import MergeStrategy

from .bids_model import BidsBuilder, BidsConfig, BidsEntity, BidsModel

LOG = logging.getLogger(__name__)


class BidsWriter:
    """Writer for BIDS Model."""

    def __init__(
        self,
        bids_root: Path,
        entity_merge_strategy: MergeStrategy,
        bids: Optional[BidsModel] = None,
        config: BidsConfig = BidsConfig.default(),
    ) -> None:
        """Initialize BIDS writer."""
        self._bids_root = bids_root
        self._entity_merge_strategy = entity_merge_strategy
        self._bids = bids
        self._builder: Optional[BidsBuilder] = None
        self._config = config

    def __enter__(self) -> BidsWriter:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Exit context manager."""
        return self.write()

    def builder(self) -> BidsBuilder:
        """Return BIDS builder, creating new if does not already exist."""
        if self._builder is None:
            self._builder = BidsBuilder()
        return self._builder

    def _merge_json(self, path: Path, data: Dict[str, str]) -> None:
        """Merge JSON file with BIDS structure."""
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_data.update(data)
            data = existing_data
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _merge_tsv(self, path: Path, data: pd.DataFrame) -> None:
        """Merge TSV file with BIDS structure."""
        if path.exists():
            existing_data = pd.read_csv(path, sep="\t")
            data = pd.concat([existing_data, data])
        data.to_csv(path, sep="\t", index=False)

    def _ensure_directory_path(self, path: Path, is_dir: bool = False) -> None:
        """Ensure directory path, or path to parent dir of file exists, or create."""
        if is_dir:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        else:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)

    def _merge_entity(
        self, entity: BidsEntity, write_op: Callable[[Path], None]
    ) -> None:
        """Write file respecting MergeStrategy."""
        expected_filepath = self._bids_root / self._config.relative_entity_path(entity)
        if (
            self._entity_merge_strategy == MergeStrategy.NO_MERGE
            and expected_filepath.exists()
        ):
            raise ValueError(f"File {expected_filepath} already exists.")
        elif self._entity_merge_strategy == MergeStrategy.OVERWRITE:
            self._ensure_directory_path(expected_filepath)
            write_op(expected_filepath)
            if entity.metadata:
                self._merge_json(
                    self._bids_root
                    / self._config.relative_entity_metadata_path(entity),
                    entity.metadata,
                )
            return
        elif self._entity_merge_strategy == MergeStrategy.KEEP:
            return
        else:
            raise ValueError(f"Unknown merge strategy {self._entity_merge_strategy}.")

    def write(self) -> bool:
        """Write BIDS structure to disk."""
        if self._bids is None and self._builder is None:
            raise ValueError("No BIDS model or builder to write.")

        if self._bids is None and self._builder is not None:
            self._bids = self._builder.build()

        # Unwrap Optional value for type-checking.
        if self._bids is None:
            raise ValueError("No BIDS model to write.")

        # Write BIDS structure
        # Confirm root
        LOG.info(f"Writing BIDS structure to {self._bids_root}")
        self._ensure_directory_path(self._bids_root, is_dir=True)
        if len(list(self._bids_root.iterdir())) > 0:
            if self._entity_merge_strategy == MergeStrategy.NO_MERGE:
                raise ValueError("BIDS root is not empty, cannot merge.")

        # Write dataset_description.json
        LOG.info("Writing dataset_description.json")
        data_description_path = self._bids_root / "dataset_description.json"
        if not data_description_path.exists() or self._config.merge_dataset_description:
            self._merge_json(data_description_path, self._bids.dataset_description)

        # Write participants.tsv
        LOG.info("Writing participants.tsv")
        participants_path = self._bids_root / "participants.tsv"
        if not participants_path.exists() or self._config.merge_participants_tsv:
            self._merge_tsv(
                participants_path, pd.DataFrame({"participant": self._bids.subject_ids})
            )

        # Write subject folders
        for entity in self._bids.entities:
            if entity.file_path is not None:
                LOG.info(f"Writing Path entity {entity.subject_id}")
                fp = entity.file_path
                self._merge_entity(entity, lambda path: shutil.copy2(fp, path))
            elif entity.tabular_data is not None:
                LOG.info(f"Writing tabular data entity {entity.subject_id}")
                tb = entity.tabular_data
                self._merge_entity(
                    entity,
                    lambda path: tb.to_csv(path, sep="\t", index=False),
                )
            else:
                raise ValueError(f"Unknown entity type for {entity}")
        return True
