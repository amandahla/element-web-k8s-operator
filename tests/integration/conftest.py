# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for Element Web charm integration tests."""

import asyncio
import json

import juju
import pytest
import pytest_asyncio
from pytest_operator.plugin import OpsTest


@pytest_asyncio.fixture(scope="module", name="model")
async def model_fixture(ops_test: OpsTest) -> juju.model.Model:
    """Provide current test model."""
    assert ops_test.model
    model_config = {"logging-config": "<root>=INFO;unit=DEBUG"}
    await ops_test.model.set_config(model_config)
    return ops_test.model


@pytest_asyncio.fixture(scope="module", name="get_unit_ips")
async def fixture_get_unit_ips(ops_test: OpsTest):
    """Return an async function to retrieve unit ip addresses of a certain application."""

    async def _get_unit_ips(application_name: str):
        """Retrieve unit ip addresses of a certain application.

        Returns:
            a list containing unit ip addresses.
        """
        _, status, _ = await ops_test.juju("status", "--format", "json")
        status = json.loads(status)
        units = status["applications"][application_name]["units"]
        return (
            unit_status["address"]
            for _, unit_status in sorted(units.items(), key=lambda kv: int(kv[0].split("/")[-1]))
        )

    yield _get_unit_ips


@pytest_asyncio.fixture(scope="module", name="element_web")
async def element_web_fixture(
    ops_test: OpsTest,
    pytestconfig: pytest.Config,
    model: juju.model.Model,
):
    """Build and deploy the Element Web charm."""
    app_name = "element-web-k8s"
    charm = await ops_test.build_charm(".")
    resources = {"element-web-image": pytestconfig.getoption("--element-web-image")}
    deploy_result = await asyncio.gather(
        model.deploy(charm, resources=resources, application_name=app_name, series="jammy"),
        model.wait_for_idle(apps=[app_name], raise_on_blocked=True),
    )
    return deploy_result[0]
