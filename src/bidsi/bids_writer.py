"""Writer for BIDS Model."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from types import TracebackType
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar

import pandas as pd

from .bids_config import BidsConfig, MergeStrategy
from .bids_model import BidsBuilder, BidsEntity, BidsModel

LOG = logging.getLogger(__name__)

# TypeVar for generic BidsWriter._merge
T = TypeVar("T", dict[str, str], pd.DataFrame, Path)


class BidsVirtualNode:
    """Virtual File Tree for BIDS Model.

    Enable constructing the BIDS file structure in memory before writing to disk.
    """

    def __init__(self, path: Path, write: bool, write_op: Callable[[], None]) -> None:
        """Initialize BidsVirtualNode."""
        raise NotImplementedError("BidsVirtualNode not implemented.")
        # self._path = path
        # self._write = write
        # self._write_op = write_op
        # self._children = []


class BidsWriter:
    """Writer for BIDS Model."""

    DATASET_DESCRIPTION_FILENAME = "dataset_description.json"
    PARTICIPANTS_FILENAME = "participants.tsv"

    def __init__(
        self,
        bids_root: Path,
        config: BidsConfig = BidsConfig.default(),
        bids: Optional[BidsModel] = None,
    ) -> None:
        """Initialize BIDS writer."""
        self._bids_root = bids_root
        self._bids = bids
        self._builder: Optional[BidsBuilder] = None
        self._config = config

    def __enter__(self) -> BidsWriter:
        """Enter context manager."""
        LOG.debug("Entering BidsWriter context manager.")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Write structure on context manager exit."""
        LOG.debug("Exiting BidsWriter context manager.")
        return self.write()

    def builder(self) -> BidsBuilder:
        """Return BIDS builder, creating new if does not already exist."""
        if self._builder is None:
            LOG.debug("Creating new BidsBuilder.")
            self._builder = BidsBuilder()
        return self._builder

    def _ensure_directory_path(self, path: Path, is_dir: bool = False) -> None:
        """Ensure directory path, or path to parent dir of file exists, or create."""
        if is_dir:
            if not path.exists():
                LOG.debug(f"Creating directory: {path}")
                path.mkdir(parents=True, exist_ok=True)
        else:
            if not path.parent.exists():
                LOG.debug(f"Creating parent directory path for file: {path}")
                path.parent.mkdir(parents=True, exist_ok=True)

    def _merge_tabular(self, path: Path, data: pd.DataFrame) -> None:
        """Merge TSV file with BIDS structure."""
        if path.exists():
            LOG.debug(f"Merging tabular data with data at {path}")
            existing_data = pd.read_csv(path, sep="\t")
            data = pd.concat([existing_data, data])
        return data

    def _write_tabular(self, path: Path, data: pd.DataFrame) -> None:
        """Write TSV file to path."""
        LOG.debug(f"Writing tabular data to {path}")
        data.to_csv(path, sep="\t", index=False)

    def _merge_file(self, path: Path, file: Path) -> Path:
        """Checks that path does not exist, and returns file."""
        if path.exists():
            raise ValueError(
                f"File resources cannot be merged. "
                f"{path} already exists, and cannot be overwritten by {file}."
            )
        return file

    def _write_file(self, path: Path, file: Path) -> None:
        """Write file to path."""
        LOG.debug(f"Copying file ({file}) to {path}")
        shutil.copy2(file, path)

    def _merge_json(self, path: Path, data: Dict[str, str]) -> Dict[str, str]:
        """Merge JSON file with BIDS structure."""
        LOG.debug(f"Merging JSON data with data at {path}")
        with path.open("r", encoding="utf-8") as f:
            existing_data = json.load(f)
        existing_data.update(data)
        return existing_data

    def _write_json(self, path: Path, data: Dict[str, str]) -> None:
        """Write JSON file to path."""
        LOG.debug(f"Writing JSON data to {path}")
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _merge(
        self,
        path: Path,
        resource: T,
        merge_strategy: MergeStrategy,
        merge_op: Callable[[Path, T], T],
        write_op: Callable[[Path, T], None],
    ) -> None:
        """Merge file with BIDS structure respecting Merge config."""
        LOG.debug(f"Merging resource to {path}")
        if path.exists():
            match merge_strategy:
                case MergeStrategy.NO_MERGE:
                    raise ValueError(f"File {path} already exists.")
                case MergeStrategy.OVERWRITE:
                    write_op(path, resource)
                case MergeStrategy.KEEP:
                    return
                case MergeStrategy.RENAME_SEQUENTIAL:
                    # Set Path to new file with run-label increment
                    pass
                case MergeStrategy.MERGE:
                    merged_resource = merge_op(path, resource)
                    write_op(path, merged_resource)

    def _merge_entity(self, entity: BidsEntity, dir: Path) -> None:
        """Write file respecting MergeStrategy."""
        expected_filepath = dir / self._config.entity.entity_name(entity)
        LOG.debug(f"Merging entity to {expected_filepath}")
        self._ensure_directory_path(expected_filepath)
        if entity.file_path is not None:
            self._merge(
                expected_filepath,
                entity.file_path,
                self._config.merge.entity,
                self._merge_file,
                self._write_file,
            )
        elif entity.tabular_data is not None:
            self._merge(
                expected_filepath,
                entity.tabular_data,
                self._config.merge.entity,
                self._merge_tabular,
                self._write_tabular,
            )
        else:
            raise ValueError(f"Unknown entity type for {entity}")
        if entity.metadata:
            expected_metadata_filepath = dir / self._config.entity.entity_metadata_name(
                entity
            )
            LOG.debug(f"Merging metadata for {entity}")
            self._merge(
                expected_metadata_filepath,
                entity.metadata,
                self._config.merge.entity_metadata,
                self._merge_json,
                self._write_json,
            )
        return

    def _merge_folder(
        self, path: Path, merge_strategy: MergeStrategy
    ) -> Tuple[Path, bool]:
        """Merge folder respecting MergeStrategy."""
        LOG.debug(f"Merging folder to {path} with strategy {merge_strategy}")
        match merge_strategy:
            case MergeStrategy.NO_MERGE:
                if path.exists():
                    if not path.is_dir():
                        raise ValueError(f"Path {path} is not a directory.")
                    if len(list(path.iterdir())) > 0:
                        raise ValueError(
                            f"Folder {path} is not empty "
                            "and merge_strategy is NO_MERGE."
                        )
                # Path does not exist or is empty. Create directory for writing.
                self._ensure_directory_path(path, is_dir=True)
                return path, True
            case MergeStrategy.OVERWRITE:
                # Remove and recreate directory.
                shutil.rmtree(path, ignore_errors=True)
                self._ensure_directory_path(path, is_dir=True)
                return path, True
            case MergeStrategy.KEEP:
                self._ensure_directory_path(path, is_dir=True)
                return path, False
            case MergeStrategy.RENAME_SEQUENTIAL:
                # TODO: Return folder with run-label increment
                raise NotImplementedError(
                    "RENAME_SEQUENTIAL merge for directories not implemented."
                )
            case MergeStrategy.MERGE:
                self._ensure_directory_path(path, is_dir=True)
                return path, True

    def write(self) -> bool:
        """Write BIDS structure to disk."""
        if self._bids is None and self._builder is None:
            raise ValueError("No BIDS model or builder to write.")

        if self._bids is None and self._builder is not None:
            self._bids = self._builder.build()

        # Unwrap Optional value for type-checking.
        if self._bids is None:
            raise ValueError("No BIDS model to write.")

        ### Write BIDS structure ###
        LOG.info(f"Writing BIDS structure to {self._bids_root}")
        self._ensure_directory_path(self._bids_root, is_dir=True)
        if len(list(self._bids_root.iterdir())) > 0:
            if self._config.merge.bids == MergeStrategy.NO_MERGE:
                raise ValueError("BIDS root is not empty, cannot merge.")

        # Write dataset_description.json
        LOG.info("Writing dataset_description.json")
        data_description_path = self._bids_root / self.DATASET_DESCRIPTION_FILENAME
        self._merge(
            data_description_path,
            self._bids.dataset_description,
            self._config.merge.dataset_description,
            self._merge_json,
            self._write_json,
        )

        # Write participants.tsv
        LOG.info("Writing participants.tsv")
        participants_path = self._bids_root / self.PARTICIPANTS_FILENAME
        # TODO: Way to incorporate participant data in addition to subject_ids.
        self._merge(
            participants_path,
            pd.DataFrame({"participant": self._bids.subject_ids}),
            self._config.merge.participants,
            self._merge_tabular,
            self._write_tabular,
        )

        # Derive subject directories, and whether to write to them.
        # subject_dirs: {subject_id: (path, write_to_dir)}
        subject_dirs = dict(
            [
                (
                    entity.subject_id,
                    self._merge_folder(
                        self._bids_root / f"sub-{entity.subject_id}",
                        self._config.merge.subject_dir,
                    ),
                )
                for entity in self._bids.entities
            ]
        )

        # Derive session directories, and whether to write to them.
        # TODO: Handle session_ids.
        # TODO: session_id default and increment.
        # session_dirs: {(subject_id, session_id): (path, write_to_dir)}
        # session_dirs = dict(
        #     [
        #         (
        #             (entity.subject_id, entity.session_id),
        #             self._merge_folder(
        #               subject_dirs[entity.subject_id][0] / f"ses-{entity.session_id}",
        #                 self._config.merge.session_dir,
        #             ),
        #         )
        #         for entity in self._bids.entities
        #         if entity.session_id and subject_dirs[entity.subject_id][1]
        #     ]
        # )

        # Write entities
        for entity in self._bids.entities:
            if not subject_dirs[entity.subject_id][1]:
                LOG.info(f"Skipping entity for subject_id merge restriction: {entity}")
                continue
            # if not session_dirs[(entity.subject_id, entity.session_id)][1]:
            #    LOG.info(f"Skipping entity for session_id merge restriction: {entity}")
            #     continue
            self._merge_entity(entity, subject_dirs[entity.subject_id][0])
        return True
