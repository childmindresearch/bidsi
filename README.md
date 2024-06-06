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

```
clean_fields: bool         # if true, limit field values in output paths to alphanumeric characters.
include_session_dir: bool  # if true, include ses-<session_id> in BIDS tree. Autoincrement if no id available.
merge_config:              # object representing how to merge into existing BIDS structure.
  merge_participants: <merge_type>          # participants.tsv
  merge_dataset_description: <merge_type>   # dataset_description.json
  merge_entity_metadata: <merge_type>       # JSON sidecar for entities
  merge_entity: <merge_type>                # Entity data itself. MERGE unavailable except for TSV entities
  merge_subject_dir: <merge_type>           # Merge each subject directory
  merge_session_dir: <merge_type>           # Merge each session directory
entity_name_config:
  - name: <filter_name>         # Used for logging / debugging
    filter:                     # Select to which entities this name config applies
      - field: <field_name>     # Field of entity to filter on
        pattern: <regex>        # Pattern to match against field
    suffix: <suffix>            # Suffix to use for entities that match filters. This does not include
                                # the file extension, which will be .tsv for tabular data and copied from
                                # the original file if entity is a file.
    fields:                     # Field order in name. Uses BidsEntity field names and BidsEntity.metadata
      - subject
      - task
      - ...
  default:                      # Default naming convention. No filters, uses only default extensions.
    name: <filter_name>
    suffix: <suffix>
    fields:
      - subject
      - session
      - task
      - ...
```
```
merge_type = MERGE | OVERWRITE | KEEP | INCREMENT | NONE
```

## Links or References

- [BIDS Starter Kit](https://bids-standard.github.io/bids-starter-kit/)
