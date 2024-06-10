"""Tests for the BidsEntity model."""

from pathlib import Path

import pandas as pd

from bidsi import BidsBuilder


def test_bids_builder_default() -> None:
    """Test that BidsEntity descriptor cleans values."""
    builder = BidsBuilder()
    model = builder.build()
    assert model.entities == []
    assert model.dataset_description == {}


def test_bids_builder_add_tabular_data_resource() -> None:
    """Test that BidsEntity descriptor cleans values."""
    builder = BidsBuilder()
    builder.add(
        subject_id="01",
        datatype="func",
        task_name="task",
        resource=pd.DataFrame(),
    )
    model = builder.build()
    assert len(model.entities) == 1
    assert model.entities[0].is_tabular_data()
    assert model.entities[0].subject_id == "01"
    assert model.entities[0].datatype == "func"
    assert model.entities[0].task_name == "task"
    assert model.entities[0].tabular_data is not None
    assert model.entities[0].tabular_data.empty


def test_bids_builder_add_file_resource() -> None:
    """Test that BidsEntity descriptor cleans values."""
    builder = BidsBuilder()
    builder.add(
        subject_id="01",
        datatype="func",
        task_name="task",
        resource=Path("resource.svg"),
    )
    model = builder.build()
    print(model.entities)
    assert len(model.entities) == 1
    assert model.entities[0].is_file_resource()
    assert model.entities[0].extension() == ".svg"
    assert model.entities[0].subject_id == "01"
    assert model.entities[0].datatype == "func"
    assert model.entities[0].task_name == "task"
    assert model.entities[0].file_path == Path("resource.svg")


def test_bids_builder_resource_metadata() -> None:
    """Test that BidsBuilder handles data dictionary."""
    builder = BidsBuilder()
    builder.add(
        subject_id="01",
        datatype="func",
        task_name="task",
        resource=Path("resource.svg"),
        metadata={"key": "value"},
    )
    model = builder.build()
    assert len(model.entities) == 1
    assert model.entities[0].metadata == {"key": "value"}


def test_bids_builder_dataset_description() -> None:
    """Test that BidsBuilder handles dataset description."""
    builder = BidsBuilder()
    builder.add_dataset_description("name", "1.0.0", {"key": "value"})
    model = builder.build()
    assert model.dataset_description == {
        "Name": "name",
        "BIDSVersion": "1.0.0",
        "key": "value",
    }


# def test_bids_entity_descriptor_cleans_values() -> None:
#     """Test that BidsEntity descriptor cleans values."""
#     bids = BidsEntity(
#         subject_id="01_AZ",
#         task_name="*task*00",
#         datatype="func_",
#         run_id="1",
#         suffix=".suffix=",
#         metadata={"ke_y": "_va_lue"},
#         session_id="-01-az",
#     )
#     assert bids.subject_id == "01AZ"
#     assert bids.task_name == "task00"
#     assert bids.datatype == "func"
#     assert bids.run_id == "1"
#     assert bids.suffix == "suffix"


# def test_bids_entity_descriptor_cleans_optional_values() -> None:
#     """Test that BidsEntity descriptor cleans values."""
#     bids = BidsEntity(
#         subject_id="01_AZ",
#         task_name="*task*00",
#         datatype="func_",
#         run_id="1",
#         suffix=".suffix=",
#         metadata={"ke_y": "_va_lue"},
#         session_id="-01-az",
#     )
#     assert bids.subject_id == "01AZ"
#     assert bids.task_name == "task00"
#     assert bids.datatype == "func"
#     assert bids.run_id == "1"
#     assert bids.suffix == "suffix"
