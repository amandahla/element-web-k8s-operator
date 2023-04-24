# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Element Web charm unit tests."""

from ops.model import ActiveStatus
from ops.testing import Harness


def test_element_web_pebble_ready(harness: Harness):
    """
    arrange: charm created
    act: trigger container pebble ready event
    assert: plan is like the expected, service is running and unit status is
        active
    """
    container_name = "element-web"
    harness.begin_with_initial_hooks()
    harness.set_can_connect(harness.model.unit.containers[container_name], True)
    harness.framework.reemit()
    element_web_layer = harness.get_container_pebble_plan(container_name).to_dict()["services"][
        container_name
    ]
    assert element_web_layer == {
        "override": "replace",
        "summary": "Element Web service",
        "startup": "enabled",
        "command": "/docker-entrypoint.sh nginx -g 'daemon off;'",
    }
    service = harness.model.unit.get_container(container_name).get_service(container_name)
    assert service.is_running()
    assert harness.model.unit.status == ActiveStatus()
