"""Integration test for simulator capture flow."""

import numpy as np
import pytest

from oscilloscope_mcp.models.capture import ChannelConfig
from oscilloscope_mcp.services.registry import get_session, set_last_capture
from oscilloscope_mcp.services.session import ScopeSession
from oscilloscope_mcp.utils.measurements import compute_measurements


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_simulator_flow():
    session = ScopeSession()
    backend = session.get_backend("simulator")
    await backend.connect("sim-001")
    await backend.configure_channels([ChannelConfig(channel_id="A", range_v=2.0)])

    capture = await backend.capture_block(
        sample_rate_hz=50_000,
        sample_count=2000,
        channels=[ChannelConfig(channel_id="A", range_v=2.0)],
    )
    set_last_capture(capture)

    channel = capture.channels[0]
    metrics = compute_measurements(
        np.asarray(channel.samples_v),
        np.asarray(capture.time_s),
    )
    assert metrics["v_pp_v"] > 0
    assert get_session() is not None
