import { useState } from "react";
import { callTool } from "@/lib/api";

export default function TriggerPage() {
  const [sourceChannel, setSourceChannel] = useState("A");
  const [thresholdV, setThresholdV] = useState(0.5);
  const [mode, setMode] = useState("auto");
  const [edge, setEdge] = useState("rising");
  const [state, setState] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const run = async (operation: string, args: Record<string, unknown> = {}) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool("scope_trigger", { operation, ...args });
      const inner = res.data;
      if (!res.success || inner?.success === false) {
        setMessage(inner?.error ?? inner?.message ?? `${operation} failed`);
        return;
      }
      setMessage(inner?.message ?? `${operation} ok`);
      if (inner?.data) setState(inner.data);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : `${operation} failed`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Trigger Configuration</h1>
      <p className="text-zinc-400 mb-4">Configure the acquisition trigger (source, threshold, edge, mode).</p>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Settings</h2>
          <div className="grid grid-cols-2 gap-3">
            <label className="text-xs text-zinc-500">
              Source channel
              <select
                value={sourceChannel}
                onChange={(e) => setSourceChannel(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="CH1">CH1</option>
                <option value="CH2">CH2</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Threshold (V)
              <input
                type="number"
                step={0.1}
                value={thresholdV}
                onChange={(e) => setThresholdV(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              />
            </label>
            <label className="text-xs text-zinc-500">
              Mode
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="auto">Auto</option>
                <option value="normal">Normal</option>
                <option value="single">Single</option>
                <option value="off">Off</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Edge
              <select
                value={edge}
                onChange={(e) => setEdge(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="rising">Rising</option>
                <option value="falling">Falling</option>
              </select>
            </label>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              type="button"
              onClick={() =>
                run("set", { source_channel: sourceChannel, threshold_v: thresholdV, mode, edge })
              }
              disabled={busy}
              className="rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30 disabled:opacity-50"
            >
              Set trigger
            </button>
            <button
              type="button"
              onClick={() => run("arm")}
              disabled={busy}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
            >
              Arm
            </button>
            <button
              type="button"
              onClick={() => run("force")}
              disabled={busy}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
            >
              Force
            </button>
            <button
              type="button"
              onClick={() => run("get")}
              disabled={busy}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
            >
              Read
            </button>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Current trigger</h2>
          {state ? (
            <pre className="text-xs text-zinc-400 font-mono whitespace-pre-wrap">
              {JSON.stringify(state, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-zinc-500">No trigger state loaded yet. Set or read a trigger.</p>
          )}
        </div>
      </div>
    </div>
  );
}
