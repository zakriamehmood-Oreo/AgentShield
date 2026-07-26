from agentshield_tools.server import ping_impl


def test_ping_impl_returns_ok_status():
    assert ping_impl() == {"status": "ok"}
