import { useState } from "react";
import { callTool } from "@/lib/api";

export default function ConfigurePage() {
  const [channelId, setChannelId] = useState("A");
  const [rangeV, setRangeV] = useState(2);
  const [coupling, setCoupling] = useState("dc");
  const [offsetV, setOffsetV] = useState(0);
  const [enabled, setEnabled] = useState(true);

  const [waveform, setWaveform] = useState("sine");
  const [frequencyHz, setFrequencyHz] = useState(1000);
  const [amplitudeV, setAmplitudeV] = useState(0.8);

  const [current, setCurrent] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const run = async (operation: string, args: Record<string, unknown> = {}) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool("scope_configure", { operation, ...args });
      const inner = res.data;
      if (!res.success || inner?.success === false) {
        setMessage(inner?.error ?? inner?.message ?? `${operation} failed`);
        return;
      }
      setMessage(`${operation} ok`);
      if (operation === "get") setCurrent(inner?.data ?? null);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : `${operation} failed`);
    } finally {
      setBusy(false);
    }
  };

  const applyChannel = async () => {
    await run("channel", {
      channel_id: channelId,
      range_v: rangeV,
      coupling,
      offset_v: offsetV,
      enabled,
    });
  };

  const applyProfile = async () => {
    await run("simulator_profile", {
      waveform,
      frequency_hz: frequencyHz,
      amplitude_v: amplitudeV,
    });
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Channel Configuration</h1>
      <p className="text-zinc-400 mb-4">Configure scope channels and simulator signal profiles.</p>

      <div className="flex gap-3 mb-6">
        <button
          type="button"
          onClick={() => run("get")}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Read current config
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Channel</h2>
          <div className="grid grid-cols-2 gap-3">
            <label className="text-xs text-zinc-500">
              Channel
              <select
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="CH1">CH1</option>
                <option value="CH2">CH2</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Range (V full-scale)
              <input
                type="number"
                min={0.1}
                step={0.5}
                value={rangeV}
                onChange={(e) => setRangeV(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              />
            </label>
            <label className="text-xs text-zinc-500">
              Coupling
              <select
                value={coupling}
                onChange={(e) => setCoupling(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="dc">DC</option>
                <option value="ac">AC</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Offset (V)
              <input
                type="number"
                step={0.1}
                value={offsetV}
                onChange={(e) => setOffsetV(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              />
            </label>
          </div>
          <label className="flex items-center gap-2 mt-3 text-sm text-zinc-300">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              className="h-4 w-4 rounded border-zinc-600 bg-zinc-800 accent-amber-500"
            />
            Enabled
          </label>
          <button
            type="button"
            onClick={applyChannel}
            disabled={busy}
            className="mt-4 rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30 disabled:opacity-50"
          >
            Apply channel
          </button>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Simulator profile</h2>
          <div className="grid grid-cols-2 gap-3">
            <label className="text-xs text-zinc-500">
              Waveform
              <select
                value={waveform}
                onChange={(e) => setWaveform(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="sine">Sine</option>
                <option value="square">Square</option>
                <option value="ramp">Ramp</option>
                <option value="noise">Noise</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Frequency (Hz)
              <input
                type="number"
                min={1}
                value={frequencyHz}
                onChange={(e) => setFrequencyHz(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              />
            </label>
            <label className="text-xs text-zinc-500">
              Amplitude (V)
              <input
                type="number"
                min={0.01}
                step={0.1}
                value={amplitudeV}
                onChange={(e) => setAmplitudeV(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              />
            </label>
          </div>
          <button
            type="button"
            onClick={applyProfile}
            disabled={busy}
            className="mt-4 rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
          >
            Apply profile
          </button>
        </div>
      </div>

      {current && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Current config</h2>
          <pre className="text-xs text-zinc-400 font-mono max-h-64 overflow-auto whitespace-pre-wrap">
            {JSON.stringify(current, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
