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

## Links or References

- [https://www.wikipedia.de](https://www.wikipedia.de)
