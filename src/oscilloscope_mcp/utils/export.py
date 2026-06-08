"""Capture export helpers (CSV, summary JSON)."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from oscilloscope_mcp.models.capture import WaveformCapture


def ensure_capture_dir(path: Path) -> Path:
    """Create capture directory if missing."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def export_capture_csv(capture: WaveformCapture, output_path: Path) -> Path:
    """Write capture samples to CSV (time_s, voltage_v columns per channel)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    channels = capture.channels
    time_s = capture.time_s

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        header = ["time_s", *[f"{ch.channel_id}_v" for ch in channels]]
        writer.writerow(header)
        for idx, t in enumerate(time_s):
            row = [f"{t:.12f}"]
            for ch in channels:
                row.append(f"{ch.samples_v[idx]:.9f}")
            writer.writerow(row)
    return output_path


def export_capture_summary(capture: WaveformCapture, output_path: Path) -> Path:
    """Write capture metadata and downsampled preview to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preview_step = max(1, len(capture.time_s) // 500)
    payload: dict[str, Any] = {
        "exported_at": datetime.now(UTC).isoformat(),
        "capture": capture.model_dump(mode="json"),
        "preview": {
            "step": preview_step,
            "time_s": capture.time_s[::preview_step].tolist(),
            "channels": {ch.channel_id: np.asarray(ch.samples_v)[::preview_step].tolist() for ch in capture.channels},
        },
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def default_capture_filename(prefix: str = "capture") -> str:
    """Generate timestamped capture filename stem."""
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"
