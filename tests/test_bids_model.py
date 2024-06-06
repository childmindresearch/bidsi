"""Tests for the BidsEntity model."""

# from bidsi import BidsEntity


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
