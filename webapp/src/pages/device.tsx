import { useCallback, useEffect, useState } from "react";
import { callTool, getStatus } from "@/lib/api";

type Device = {
  device_id: string;
  backend: string;
  model: string;
  serial?: string | null;
  connected?: boolean;
  driver_status?: string;
  driver_hint?: string | null;
  capabilities?: {
    channels?: number;
    max_sample_rate_hz?: number;
    bandwidth_hz?: number | null;
    resolution_bits?: number;
    has_awg?: boolean;
    max_input_voltage_v?: number | null;
  };
};

export default function DevicePage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [backends, setBackends] = useState<string[]>([]);
  const [activeBackend, setActiveBackend] = useState<string | null>(null);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [capabilities, setCapabilities] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const st = await getStatus();
    setActiveBackend(st.active_backend ?? null);

    const listRes = await callTool("scope_device", { operation: "list" });
    if (listRes.success) setDevices(listRes.data?.data?.devices ?? []);

    const backRes = await callTool("scope_device", { operation: "backends" });
    if (backRes.success) {
      setBackends(backRes.data?.data?.backends ?? []);
      setActiveBackend(backRes.data?.data?.active ?? st.active_backend ?? null);
    }

    const statusRes = await callTool("scope_device", { operation: "status" });
    if (statusRes.success) setStatus(statusRes.data?.data ?? null);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const run = async (operation: string, extra: Record<string, unknown> = {}) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool("scope_device", { operation, ...extra });
      const inner = res.data;
      if (!res.success || inner?.success === false) {
        setMessage(inner?.error ?? inner?.message ?? `${operation} failed`);
      } else {
        setMessage(`${operation} ok`);
        await refresh();
      }
    } catch (e) {
      setMessage(e instanceof Error ? e.message : `${operation} failed`);
    }
    setBusy(false);
  };

  const showCapabilities = async () => {
    setBusy(true);
    setMessage(null);
    const res = await callTool("scope_device", { operation: "capabilities" });
    const inner = res.data;
    setCapabilities(res.success && inner?.success !== false ? (inner?.data ?? null) : null);
    if (!res.success || inner?.success === false) {
      setMessage(inner?.error ?? inner?.message ?? "Capabilities unavailable");
    }
    setBusy(false);
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Device Management</h1>
      <p className="text-zinc-400 mb-4">Discover and connect oscilloscope backends (simulator, PicoScope, Hantek).</p>

      <div className="flex gap-3 mb-6">
        <button
          type="button"
          onClick={() => run("connect", { device_id: "sim-001" })}
          disabled={busy}
          className="rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30 disabled:opacity-50"
        >
          Connect simulator
        </button>
        <button
          type="button"
          onClick={() => run("disconnect")}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Disconnect
        </button>
        <button
          type="button"
          onClick={refresh}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Refresh
        </button>
        <button
          type="button"
          onClick={showCapabilities}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Capabilities
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Connected</h2>
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`h-2 w-2 rounded-full ${status?.connected ? "bg-green-500" : "bg-zinc-600"}`}
            />
            <span className="text-sm">
              {Boolean(status?.connected) ? "Connected" : "Disconnected"}
            </span>
            {activeBackend && (
              <span className="text-xs text-zinc-500">backend: {activeBackend}</span>
            )}
          </div>
          {Boolean(status?.device) && (
            <pre className="text-xs text-zinc-400 font-mono mt-2 max-h-48 overflow-auto whitespace-pre-wrap">
              {JSON.stringify(status?.device ?? null, null, 2)}
            </pre>
          )}
          {Boolean(status?.capture_dir) && (
            <p className="text-xs text-zinc-500 mt-2">
              capture dir: {String(status?.capture_dir)}
            </p>
          )}
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Backends</h2>
          <div className="flex flex-wrap gap-2">
            {backends.map((b) => (
              <span
                key={b}
                className={`rounded-full px-3 py-1 text-xs ${
                  b === activeBackend
                    ? "bg-amber-500/20 text-amber-200"
                    : "bg-zinc-800 text-zinc-400"
                }`}
              >
                {b}
              </span>
            ))}
          </div>
          {capabilities && (
            <pre className="text-xs text-zinc-400 font-mono mt-3 max-h-48 overflow-auto whitespace-pre-wrap">
              {JSON.stringify(capabilities, null, 2)}
            </pre>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
        <h2 className="text-sm font-semibold mb-3 text-zinc-300">Discovered devices</h2>
        {devices.length === 0 ? (
          <p className="text-sm text-zinc-500">No devices reported.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {devices.map((d) => (
              <div key={d.device_id} className="rounded-lg border border-zinc-800 bg-zinc-950 p-3">
                <div className="flex items-center justify-between mb-1">
                  <p className="font-mono text-sm text-amber-200">{d.device_id}</p>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] ${
                      d.connected ? "bg-green-500/20 text-green-300" : "bg-zinc-800 text-zinc-400"
                    }`}
                  >
                    {d.connected ? "connected" : "available"}
                  </span>
                </div>
                <p className="text-xs text-zinc-400">
                  {d.model} · {d.backend}
                  {d.serial ? ` · ${d.serial}` : ""}
                </p>
                <p className="text-[11px] text-zinc-500 mt-1">
                  {d.capabilities?.channels ?? "?"} ch ·{" "}
                  {(d.capabilities?.max_sample_rate_hz ?? 0) / 1_000_000} MS/s ·{" "}
                  {d.capabilities?.resolution_bits ?? "?"} bit
                  {d.capabilities?.bandwidth_hz ? ` · ${d.capabilities.bandwidth_hz / 1e6} MHz` : ""}
                </p>
                {!d.connected && (
                  <button
                    type="button"
                    onClick={() => run("connect", { device_id: d.device_id })}
                    disabled={busy}
                    className="mt-2 rounded-md border border-zinc-700 px-3 py-1 text-xs hover:bg-zinc-800 disabled:opacity-50"
                  >
                    Connect
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
