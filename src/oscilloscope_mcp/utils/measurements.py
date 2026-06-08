"""Waveform measurement utilities (frequency, Vpp, duty cycle, rise time)."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def compute_measurements(
    samples_v: np.ndarray,
    time_s: np.ndarray,
    *,
    threshold_fraction: float = 0.5,
) -> dict[str, Any]:
    """Compute common oscilloscope measurements from voltage samples."""
    if len(samples_v) < 2:
        raise ValueError("At least 2 samples are required for measurements")

    v_min = float(np.min(samples_v))
    v_max = float(np.max(samples_v))
    v_pp = v_max - v_min
    v_mean = float(np.mean(samples_v))
    v_rms = float(np.sqrt(np.mean(np.square(samples_v))))

    dt = float(time_s[1] - time_s[0]) if len(time_s) > 1 else 0.0
    sample_rate_hz = 1.0 / dt if dt > 0 else 0.0
    duration_s = float(time_s[-1] - time_s[0]) if len(time_s) > 1 else 0.0

    result: dict[str, Any] = {
        "v_min_v": round(v_min, 6),
        "v_max_v": round(v_max, 6),
        "v_pp_v": round(v_pp, 6),
        "v_mean_v": round(v_mean, 6),
        "v_rms_v": round(v_rms, 6),
        "sample_count": len(samples_v),
        "sample_rate_hz": round(sample_rate_hz, 3),
        "duration_s": round(duration_s, 9),
    }

    if v_pp < 1e-9:
        result["frequency_hz"] = None
        result["period_s"] = None
        result["duty_cycle_pct"] = None
        result["rise_time_s"] = None
        result["note"] = "Flat signal - frequency and edge measurements skipped"
        return result

    threshold = v_min + v_pp * threshold_fraction
    above = samples_v >= threshold
    edges = np.diff(above.astype(int))
    rising_idx = np.where(edges == 1)[0]
    falling_idx = np.where(edges == -1)[0]

    if len(rising_idx) >= 2:
        period_samples = float(rising_idx[1] - rising_idx[0])
        period_s = period_samples * dt
        result["period_s"] = round(period_s, 9)
        result["frequency_hz"] = round(1.0 / period_s, 3) if period_s > 0 else None
    else:
        result["period_s"] = None
        result["frequency_hz"] = None

    if len(rising_idx) >= 1 and len(falling_idx) >= 1:
        high_samples = 0
        for rise in rising_idx:
            falls_after = falling_idx[falling_idx > rise]
            if len(falls_after) > 0:
                high_samples += int(falls_after[0] - rise)
        if result.get("period_s"):
            period_samples_est = result["period_s"] / dt if dt > 0 else 0
            if period_samples_est > 0:
                duty = 100.0 * high_samples / period_samples_est
                result["duty_cycle_pct"] = round(min(max(duty, 0.0), 100.0), 2)
            else:
                result["duty_cycle_pct"] = None
        else:
            result["duty_cycle_pct"] = None
    else:
        result["duty_cycle_pct"] = None

    low_level = v_min + 0.1 * v_pp
    high_level = v_min + 0.9 * v_pp
    rise_time_s = _estimate_rise_time(samples_v, time_s, low_level, high_level)
    result["rise_time_s"] = round(rise_time_s, 9) if rise_time_s is not None else None

    return result


def _estimate_rise_time(
    samples_v: np.ndarray,
    time_s: np.ndarray,
    low_level: float,
    high_level: float,
) -> float | None:
    """Estimate 10%-90% rise time on the first qualifying edge."""
    crossings_low = _threshold_crossings(samples_v, low_level, rising=True)
    crossings_high = _threshold_crossings(samples_v, high_level, rising=True)
    if not crossings_low or not crossings_high:
        return None

    t_low = _interpolate_crossing_time(samples_v, time_s, crossings_low[0], low_level)
    t_high = _interpolate_crossing_time(samples_v, time_s, crossings_high[0], high_level)
    if t_high <= t_low:
        return None
    return float(t_high - t_low)


def _threshold_crossings(samples_v: np.ndarray, level: float, *, rising: bool) -> list[int]:
    above = samples_v >= level
    edges = np.diff(above.astype(int))
    if rising:
        return [int(i) for i in np.where(edges == 1)[0]]
    return [int(i) for i in np.where(edges == -1)[0]]


def _interpolate_crossing_time(
    samples_v: np.ndarray,
    time_s: np.ndarray,
    index: int,
    level: float,
) -> float:
    """Linear interpolation between samples at threshold crossing."""
    v0 = float(samples_v[index])
    v1 = float(samples_v[index + 1])
    t0 = float(time_s[index])
    t1 = float(time_s[index + 1])
    if math.isclose(v1, v0):
        return t0
    fraction = (level - v0) / (v1 - v0)
    return t0 + fraction * (t1 - t0)
