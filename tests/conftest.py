# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Global fixtures and utilities for integration and unit tests."""

from pathlib import Path

import yaml


def pytest_addoption(parser):
    """Define some command line options for integration and unit tests."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("UTF-8"))
    parser.addoption(
        "--element-web-image",
        action="store",
        default=metadata["resources"]["element-web-image"]["upstream-source"],
    )
