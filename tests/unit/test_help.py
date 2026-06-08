"""Unit tests for help catalog."""

from oscilloscope_mcp.tools.portmanteau.help import _TOOLS_CATALOG


def test_tools_catalog_has_core_tools():
    expected = {
        "scope_device",
        "scope_configure",
        "scope_trigger",
        "scope_capture",
        "scope_measure",
        "scope_help",
    }
    assert expected.issubset(_TOOLS_CATALOG.keys())
