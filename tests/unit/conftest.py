# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""pytest fixtures for the integration test."""

import pytest
from ops.testing import Harness

from charm import ElementWebCharm


@pytest.fixture(name="harness")
def harness_fixture():
    """Ops testing framework harness fixture."""
    harness = Harness(ElementWebCharm)
    yield harness
    harness.cleanup()
