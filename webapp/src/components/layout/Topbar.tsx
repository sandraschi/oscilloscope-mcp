import { useQuery } from "@tanstack/react-query";
import { getStatus } from "@/lib/api";

export default function Topbar() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus, refetchInterval: 15000 });

  const connected = Boolean(status?.connected_device);
  const backend = status?.active_backend ?? "none";

  return (
    <header className="h-14 border-b border-zinc-800 bg-zinc-900/90 backdrop-blur px-6 flex items-center justify-between">
      <div>
        <h1 className="text-sm font-medium text-zinc-300">USB PC Oscilloscope Console</h1>
        <p className="text-xs text-zinc-500">Backend :10936 · Frontend :10937</p>
      </div>
      <div className="flex items-center gap-4 text-xs">
        <span className="text-zinc-500">Backend</span>
        <span className="text-blue-400 font-mono">{backend}</span>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2 py-1 ${
            connected ? "bg-emerald-500/20 text-emerald-300" : "bg-zinc-800 text-zinc-400"
          }`}
        >
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-400" : "bg-zinc-500"}`} />
          {connected ? "Connected" : "Idle"}
        </span>
      </div>
    </header>
  );
}
