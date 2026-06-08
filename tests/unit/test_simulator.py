"""Unit tests for simulator backend."""

import pytest

from oscilloscope_mcp.models.capture import ChannelConfig
from oscilloscope_mcp.services.backends.simulator import SimulatorBackend


@pytest.mark.asyncio
async def test_simulator_connect_and_capture():
    backend = SimulatorBackend()
    device = await backend.connect("sim-001")
    assert device.connected is True

    capture = await backend.capture_block(
        sample_rate_hz=100_000,
        sample_count=1000,
        channels=[ChannelConfig(channel_id="A", range_v=2.0)],
    )
    assert capture.sample_count == 1000
    assert len(capture.channels) == 1
    assert len(capture.channels[0].samples_v) == 1000
    assert capture.metadata.get("simulated") is True


@pytest.mark.asyncio
async def test_simulator_requires_connection():
    backend = SimulatorBackend()
    with pytest.raises(RuntimeError, match="No simulator device connected"):
        await backend.capture_block(sample_rate_hz=1000, sample_count=100)
