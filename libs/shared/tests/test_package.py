import agentshield_shared


def test_version_is_a_string():
    assert isinstance(agentshield_shared.__version__, str)
    assert agentshield_shared.__version__ != ""
