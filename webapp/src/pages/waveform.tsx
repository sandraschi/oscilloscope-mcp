import { useCallback, useEffect, useRef, useState } from "react";
import { callTool, runCapture } from "@/lib/api";

type Preview = {
  time_s: number[];
  channels: Record<string, number[]>;
};

export default function Waveform() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

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
      const times = data.time_s;
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
      void times;
    });

    ctx.strokeStyle = "#3f3f46";
    ctx.beginPath();
    ctx.moveTo(20, height / 2);
    ctx.lineTo(width - 20, height / 2);
    ctx.stroke();
  }, []);

  useEffect(() => {
    if (preview) draw(preview);
  }, [preview, draw]);

  const connectSimulator = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool("scope_device", { operation: "connect", device_id: "sim-001" });
      setMessage(res.data?.success ? "Connected to simulator" : res.data?.error ?? "Connect failed");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Connect failed");
    }
    setBusy(false);
  };

  const capture = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await runCapture({ sample_rate_hz: 100000, sample_count: 2000, channel_id: "A", range_v: 2 });
      const previewData = res.data?.data?.preview as Preview | undefined;
      if (previewData) setPreview(previewData);
      const measure = await callTool("scope_measure", { operation: "all", channel_id: "A" });
      setMetrics(measure.data?.data ?? null);
      setMessage("Capture complete");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Capture failed");
    }
    setBusy(false);
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Waveform Viewer</h1>
      <p className="text-zinc-400 mb-4">Live preview from scope_capture (simulator or USB hardware).</p>

      <div className="flex gap-3 mb-4">
        <button
          type="button"
          onClick={connectSimulator}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Connect simulator
        </button>
        <button
          type="button"
          onClick={capture}
          disabled={busy}
          className="rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30 disabled:opacity-50"
        >
          Capture
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 mb-6">
        <canvas ref={canvasRef} width={960} height={360} className="w-full rounded-lg" />
      </div>

      {metrics && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          {Object.entries(metrics).map(([key, value]) => (
            <div key={key}>
              <p className="text-zinc-500 text-xs">{key}</p>
              <p className="font-mono text-amber-200">{String(value)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
