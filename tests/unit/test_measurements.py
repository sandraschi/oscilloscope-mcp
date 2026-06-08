"""Unit tests for waveform measurements."""

import numpy as np
import pytest

from oscilloscope_mcp.utils.measurements import compute_measurements


def test_sine_measurements():
    sample_rate = 100_000
    frequency = 1_000
    duration = 0.01
    count = int(sample_rate * duration)
    t = np.arange(count) / sample_rate
    samples = 0.8 * np.sin(2 * np.pi * frequency * t)

    metrics = compute_measurements(samples, t)
    assert metrics["v_pp_v"] == pytest.approx(1.6, rel=0.05)
    assert metrics["frequency_hz"] == pytest.approx(1000, rel=0.05)


def test_flat_signal_skips_frequency():
    samples = np.ones(100) * 1.5
    t = np.arange(100) / 1000
    metrics = compute_measurements(samples, t)
    assert metrics["frequency_hz"] is None
    assert "note" in metrics
