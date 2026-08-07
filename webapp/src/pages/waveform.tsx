import { useCallback, useEffect, useRef, useState } from "react";
import { callTool, getLastCapture, getStatus, runCapture } from "@/lib/api";

type Preview = {
  sample_rate_hz?: number;
  sample_count?: number;
  time_s: number[];
  channels: Record<string, number[]>;
};

export default function Waveform() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [backend, setBackend] = useState<string | null>(null);

  const [sampleRateHz, setSampleRateHz] = useState(100_000);
  const [sampleCount, setSampleCount] = useState(2000);
  const [channelId, setChannelId] = useState("A");
  const [rangeV, setRangeV] = useState(2);
  const [measureChannel, setMeasureChannel] = useState("A");
  const [filename, setFilename] = useState("");

  const draw = useCallback((data: Preview) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#09090b";
    ctx.fillRect(0, 0, width, height);

    const colors = ["#f59e0b", "#3b82f6", "#10b981", "#ef4444"];
    const channelIds = Object.keys(data.channels);
    if (!channelIds.length) return;

    let min = Infinity;
    let max = -Infinity;
    for (const id of channelIds) {
      for (const v of data.channels[id]) {
        min = Math.min(min, v);
        max = Math.max(max, v);
      }
    }
    const span = max - min || 1;

    channelIds.forEach((id, index) => {
      const samples = data.channels[id];
      ctx.strokeStyle = colors[index % colors.length];
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      samples.forEach((v, i) => {
        const x = (i / Math.max(samples.length - 1, 1)) * (width - 40) + 20;
        const y = height - 20 - ((v - min) / span) * (height - 40);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.fillStyle = colors[index % colors.length];
      ctx.fillText(`CH ${id}`, 24, 20 + index * 16);
    });

    ctx.strokeStyle = "#3f3f46";
    ctx.beginPath();
    ctx.moveTo(20, height / 2);
    ctx.lineTo(width - 20, height / 2);
    ctx.stroke();

    if (data.sample_rate_hz) {
      ctx.fillStyle = "#71717a";
      ctx.font = "10px monospace";
      ctx.fillText(`${data.sample_rate_hz} S/s`, width - 120, height - 8);
    }
  }, []);

  useEffect(() => {
    if (preview) draw(preview);
  }, [preview, draw]);

  useEffect(() => {
    (async () => {
      const st = await getStatus();
      setBackend(st.active_backend ?? null);
      const last = await getLastCapture();
      if (last.success && last.data?.preview) {
        const p = last.data.preview as Preview;
        if (last.data?.capture) {
          p.sample_rate_hz = last.data.capture.sample_rate_hz ?? p.sample_rate_hz;
          p.sample_count = last.data.capture.sample_count ?? p.sample_count;
        }
        setPreview(p);
        setMessage("Loaded last capture");
      }
    })();
  }, []);

  const capture = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await runCapture({ sample_rate_hz: sampleRateHz, sample_count: sampleCount, channel_id: channelId, range_v: rangeV });
      const previewData = res.data?.data?.preview as Preview | undefined;
      if (previewData) {
        setPreview(previewData);
        setSampleRateHz(previewData.sample_rate_hz ?? sampleRateHz);
        setSampleCount(previewData.sample_count ?? sampleCount);
      }
      setMessage("Capture complete");
      await measure(channelId);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Capture failed");
    }
    setBusy(false);
  };

  const measure = async (ch: string) => {
    const res = await callTool("scope_measure", { operation: "all", channel_id: ch });
    const inner = res.data;
    if (res.success && inner?.success !== false && inner?.data) setMetrics(inner.data);
    else setMessage(inner?.error ?? inner?.message ?? "Measure failed");
  };

  const exportFile = async (operation: string) => {
    setBusy(true);
    setMessage(null);
    const stem = filename.trim() || undefined;
    const res = await callTool("scope_capture", { operation, filename: stem });
    const inner = res.data;
    if (res.success && inner?.success !== false && inner?.data?.path) {
      setMessage(`Exported to ${inner.data.path}`);
    } else {
      setMessage(inner?.error ?? inner?.message ?? "Export failed — run a capture first");
    }
    setBusy(false);
  };

  const metricsLabels: Record<string, string> = {
    v_pp_v: "Vpp (V)",
    v_min_v: "Vmin (V)",
    v_max_v: "Vmax (V)",
    v_avg_v: "Vavg (V)",
    frequency_hz: "Frequency (Hz)",
    period_s: "Period (s)",
    duty_cycle_pct: "Duty (%)",
    rise_time_s: "Rise time (s)",
    fall_time_s: "Fall time (s)",
  };

  return (
    <div className="max-w-6xl">
      <div className="flex items-center gap-3 mb-2">
        <h1 className="text-2xl font-bold">Waveform Viewer</h1>
        {backend && (
          <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] text-zinc-400">
            backend: {backend}
          </span>
        )}
      </div>
      <p className="text-zinc-400 mb-4">Acquire and visualize waveforms (simulator or USB hardware).</p>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-4 items-end">
        <label className="text-xs text-zinc-500 col-span-2">
          Sample rate
          <select
            value={sampleRateHz}
            onChange={(e) => setSampleRateHz(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={10_000}>10 kS/s</option>
            <option value={100_000}>100 kS/s</option>
            <option value={1_000_000}>1 MS/s</option>
            <option value={10_000_000}>10 MS/s</option>
          </select>
        </label>
        <label className="text-xs text-zinc-500 col-span-2">
          Sample count
          <select
            value={sampleCount}
            onChange={(e) => setSampleCount(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={500}>500</option>
            <option value={2000}>2 000</option>
            <option value={4000}>4 000</option>
            <option value={10000}>10 000</option>
          </select>
        </label>
        <label className="text-xs text-zinc-500">
          Channel
          <select
            value={channelId}
            onChange={(e) => setChannelId(e.target.value)}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value="A">A</option>
            <option value="B">B</option>
          </select>
        </label>
        <label className="text-xs text-zinc-500">
          Range (V)
          <select
            value={rangeV}
            onChange={(e) => setRangeV(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
          </select>
        </label>
      </div>

      <div className="flex gap-3 mb-6">
        <button
          type="button"
          onClick={capture}
          disabled={busy}
          className="rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30 disabled:opacity-50"
        >
          Capture
        </button>
        <button
          type="button"
          onClick={() => measure(measureChannel)}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Measure
        </button>
        <select
          value={measureChannel}
          onChange={(e) => setMeasureChannel(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
        >
          <option value="A">A</option>
          <option value="B">B</option>
        </select>
        <input
          type="text"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          placeholder="export filename stem"
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
        />
        <button
          type="button"
          onClick={() => exportFile("export_csv")}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Export CSV
        </button>
        <button
          type="button"
          onClick={() => exportFile("export_summary")}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Export summary
        </button>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 mb-6">
        <canvas ref={canvasRef} width={960} height={360} className="w-full rounded-lg" />
        {!preview && (
          <p className="text-sm text-zinc-500 text-center py-8">No waveform yet. Run a capture.</p>
        )}
      </div>

      {preview && (preview.sample_rate_hz || preview.sample_count) && (
        <div className="flex gap-4 text-xs text-zinc-500 mb-6">
          <span>{preview.sample_rate_hz?.toLocaleString()} S/s</span>
          <span>{preview.sample_count?.toLocaleString()} samples</span>
          <span>{Object.keys(preview.channels).length} channel(s)</span>
        </div>
      )}

      {metrics && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key}>
              <p className="text-zinc-500 text-xs">{metricsLabels[key] ?? key}</p>
              <p className="font-mono text-amber-200">
                {typeof value === "number" ? value.toPrecision(4) : String(value)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
