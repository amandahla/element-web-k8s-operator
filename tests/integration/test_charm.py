#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for Element Web charm."""

import logging

import juju
import requests
from ops.model import ActiveStatus, Application
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


async def test_element_web_is_up(element_web, get_unit_ips):
    """
    arrange: build and deploy the Element Web charm.
    act: send a request to the Element Web application managed by the Element Web charm.
    assert: the Element Web application should return a correct response.
    """
    for unit_ip in await get_unit_ips(element_web.name):
        response = requests.get(f"http://{unit_ip}", timeout=5)
        assert response.status_code == 200


async def test_with_ingress(
    ops_test: OpsTest,
    model: juju.model.Model,
    element_web: Application,
    get_unit_ips,
):
    """
    arrange: build and deploy the Element Web charm.
    act: deploy the ingress, configure it and relate it to the charm.
    assert: requesting the charm through traefik should return a correct response
    """
    traefik_app = await model.deploy("traefik-k8s", trust=True)
    await model.wait_for_idle()

    external_hostname = "juju.local"
    await traefik_app.set_config(
        {
            "external_hostname": external_hostname,
            "routing_mode": "subdomain",
        }
    )
    await model.wait_for_idle()

    await model.add_relation(element_web.name, traefik_app.name)

    # mypy doesn't see that ActiveStatus has a name
    await model.wait_for_idle(status=ActiveStatus.name)  # type: ignore

    traefik_ip = next(await get_unit_ips(traefik_app.name))
    response = requests.get(
        f"http://{traefik_ip}",
        headers={"Host": f"{ops_test.model_name}-{element_web.name}.{external_hostname}"},
        timeout=5,
    )
    assert response.status_code == 200
