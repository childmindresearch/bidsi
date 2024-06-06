"""Test for BidsConfig loading."""

import pytest
from pydantic import ValidationError

from bidsi import BidsConfig, MergeStrategy

TEST_CONFIG = """
[structure]
clean_fields = true
include_session_dir = false

[merge]
participants = "MERGE"
dataset_description = "OVERWRITE"
entity_metadata = "OVERWRITE"
entity = "OVERWRITE"
subject_dir = "OVERWRITE"
session_dir = "OVERWRITE"

[entity]
default_template = ["subject", "task", "suffix"]

[[entity.templates]]
name = "name"
suffix = "suffix"
fields = ["subject", "task", "suffix"]

[[entity.templates.filters]]
field = "task"
pattern = "regex"

[[entity.templates]]
name = "name2"
suffix = "suffix2"
fields = ["subject", "suffix"]

[[entity.templates.filters]]
field = "subject"
pattern = "regex2"
"""

TEST_CONFIG_UNKNOWN_KEYWORD_ERROR = """
[[entity.template]]
name = "name"
suffix = "suffix"
fields = ["subject", "task", "suffix"]
"""

TEST_CONFIG_UNKNOWN_MERGE_ENUM = """
[merge]
participants = "MERG"
"""


def test_bids_config_from_string() -> None:
    """Test that BidsEntity descriptor cleans values."""
    config = BidsConfig.from_string(TEST_CONFIG)
    assert config.structure.clean_fields is True
    assert config.structure.include_session_dir is False
    assert config.merge.participants == MergeStrategy.MERGE
    assert config.merge.dataset_description == MergeStrategy.OVERWRITE
    assert config.merge.entity_metadata == MergeStrategy.OVERWRITE
    assert config.merge.entity == MergeStrategy.OVERWRITE
    assert config.merge.subject_dir == MergeStrategy.OVERWRITE
    assert config.merge.session_dir == MergeStrategy.OVERWRITE
    assert config.entity.default_template == ["subject", "task", "suffix"]
    assert len(config.entity.templates) == 2
    assert config.entity.templates[0].name == "name"
    assert config.entity.templates[1].name == "name2"


def test_bids_config_unknown_keyword_error() -> None:
    """Test that incorrect config produces error."""
    with pytest.raises(ValidationError):
        BidsConfig.from_string(TEST_CONFIG_UNKNOWN_KEYWORD_ERROR)


def test_bids_config_unknown_merge_enum_error() -> None:
    """Test that incorrect config produces error."""
    with pytest.raises(ValidationError):
        BidsConfig.from_string(TEST_CONFIG_UNKNOWN_MERGE_ENUM)
