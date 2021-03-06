import pytest


@pytest.fixture(scope="module")
def containers():
    yield [
        {
            "name": "mycoolwebcontainer",
            "image": "nginx:latest",
            "resources": {"requests": {"memory_in_gb": 1.0, "cpu": 1.0,}},
            "ports": [],
            "environment_variables": [],
        }
    ]


@pytest.mark.asyncio
@pytest.mark.run(order=2)
async def test_present(hub, ctx, resource_group, location, containers):
    aci = "aci-idemtest"
    expected = {
        "changes": {
            "new": {
                "name": aci,
                "containers": containers,
                "location": location,
                "os_type": "Linux",
                "restart_policy": "OnFailure",
                "sku": "Standard",
                "tags": {"hihi": "cats"},
                "provisioning_state": "Succeeded",
                "init_containers": [],
                "instance_view": {"events": [], "state": "Running"},
                "type": "Microsoft.ContainerInstance/containerGroups",
            },
            "old": {},
        },
        "comment": f"Container instance group {aci} has been created.",
        "name": aci,
        "result": True,
    }
    ret = await hub.states.azurerm.containerinstance.group.present(
        ctx,
        aci,
        resource_group,
        containers=containers,
        os_type="Linux",
        tags={"hihi": "cats"},
    )
    ret["changes"]["new"].pop("id")
    ret["changes"]["new"]["containers"][0].pop("instance_view")
    assert ret == expected


@pytest.mark.run(order=2, after="test_present", before="test_absent")
@pytest.mark.asyncio
async def test_changes(hub, ctx, resource_group, location, containers, tags):
    aci = "aci-idemtest"
    expected = {
        "changes": {"tags": {"new": tags, "old": {"hihi": "cats"}},},
        "comment": f"Container instance group {aci} has been updated.",
        "name": aci,
        "result": True,
    }
    ret = await hub.states.azurerm.containerinstance.group.present(
        ctx, aci, resource_group, containers=containers, os_type="Linux", tags=tags,
    )
    assert ret == expected


@pytest.mark.run(order=-2)
@pytest.mark.asyncio
async def test_absent(hub, ctx, resource_group, location, containers, tags):
    aci = "aci-idemtest"
    expected = {
        "changes": {
            "new": {},
            "old": {
                "location": location,
                "name": aci,
                "os_type": "Linux",
                "provisioning_state": "Succeeded",
                "restart_policy": "OnFailure",
                "sku": "Standard",
                "type": "Microsoft.ContainerInstance/containerGroups",
                "tags": tags,
                "containers": containers,
                "init_containers": [],
                "instance_view": {"events": [], "state": "Running"},
            },
        },
        "comment": f"Container instance group {aci} has been deleted.",
        "name": aci,
        "result": True,
    }
    ret = await hub.states.azurerm.containerinstance.group.absent(
        ctx, aci, resource_group
    )
    ret["changes"]["old"].pop("id")
    for cnt in ret["changes"]["old"].get("containers", []):
        cnt.pop("instance_view")
    assert ret == expected
