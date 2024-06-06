[![DOI](https://zenodo.org/badge/657341621.svg)](https://zenodo.org/doi/10.5281/zenodo.10383685)

# CMI Bidsi Repository

Welcome to the CMI Bidsi Repository!

# Bidsi


[![Build](https://github.com/childmindresearch/bidsi/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/childmindresearch/bidsi/actions/workflows/test.yaml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/childmindresearch/bidsi/branch/main/graph/badge.svg?token=22HWWFWPW5)](https://codecov.io/gh/childmindresearch/bidsi)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![stability-stable](https://img.shields.io/badge/stability-stable-green.svg)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/childmindresearch/bidsi/blob/main/LICENSE)
[![pages](https://img.shields.io/badge/api-docs-blue)](https://childmindresearch.github.io/bidsi)

Bidsi is a library to facilitate converting a variety of data sources to BIDS format. The library is not intended to know anything about the incoming dataset, but rather provides the classes and utilities to build and write BIDS structured data.

## Features

- BIDS Builder class to programmatically construct a BIDS Model.
- BIDS Writer class to write out BIDS Model, as well as merge with existing BIDS structure.

## Installation

Install this package via :

```sh
pip install git+https://github.com/childmindresearch/bidsi
```

## Quick start

```Python
import bidsi

with bidsi.BidsWriter(Path("/home/bids/root/dir"), bidsi.MergeStrategy.OVERWRITE) as writer:
  builder = writer.builder()
  builder.add(...)

```

## Configuration

```toml
[structure]
clean_fields = true          # if true, limit field values in output paths to alphanumeric characters.
include_session_dir = false  # if true, include ses-<session_id> in BIDS tree. Autoincrement if no id available.

[merge]      # object representing how to merge into existing BIDS structure.
participants = "MERGE"                # participants.tsv
dataset_description = "OVERWRITE"     # dataset_description.json
entity_metadata = "OVERWRITE"         # JSON sidecar for entities
entity = "OVERWRITE"                  # Entity data itself. MERGE unavailable except for TSV entities
subject_dir = "OVERWRITE"             # Merge each subject directory
session_dir = "OVERWRITE"             # Merge each session directory

[entity]       # Entity config. Controls how specific BIDS entities are named, referencing fields of BidsEntity and metadata.
default_template = ["subject", "task", "suffix"]     # Default fields included in name.

[[entity.templates]]       # List of templates for specific entity types.
name = "name"              # Name of this entity type, for debugging.
suffix = "suffix"          # Suffix for this entity type.
fields = ["subject", "task", "suffix"]       # Fields included in entity file name.

[[entity.templates.filters]]  # List of filter specifications for which entity types the above template applies.
field = "task"                # Field to match.
pattern = "regex"             # Pattern to match against field.

[[entity.templates]]       # Second entity template example.
name = "name2"
suffix = "suffix2"
fields = ["subject", "suffix"]

[[entity.templates.filters]]
field = "subject"
pattern = "regex2"
```
```
merge_type = MERGE | OVERWRITE | KEEP | INCREMENT | NONE
```

## Links or References

- [BIDS Starter Kit](https://bids-standard.github.io/bids-starter-kit/)
