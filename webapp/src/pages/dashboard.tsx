import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getCapabilities, getStatus } from "@/lib/api";

export default function Dashboard() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus });
  const { data: caps } = useQuery({ queryKey: ["capabilities"], queryFn: getCapabilities });

  const portmanteau = caps?.tool_surface?.portmanteau_tools ?? [];

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
      <p className="text-zinc-400 mb-6">Fleet oscilloscope console - simulator, PicoScope, and Hantek backends.</p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Tools" value={String(status?.tool_count ?? "-")} accent="text-blue-400" />
        <StatCard label="Backend" value={status?.active_backend ?? "auto"} accent="text-amber-400" />
        <StatCard label="Portmanteau" value={String(caps?.tool_surface?.portmanteau_count ?? "-")} accent="text-emerald-400" />
        <StatCard label="Version" value={status?.version ?? "-"} accent="text-zinc-200" />
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">Quick actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link to="/waveform" className="rounded-lg bg-amber-500/20 text-amber-200 px-4 py-2 text-sm hover:bg-amber-500/30">
            Open waveform viewer
          </Link>
          <Link to="/tools" className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800">
            Browse MCP tools
          </Link>
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
        <h2 className="text-lg font-semibold mb-3">Portmanteau tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {portmanteau.map((tool) => (
            <div key={tool} className="rounded-lg border border-zinc-800 p-3">
              <p className="font-mono text-amber-300 text-sm">{tool}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
      <p className="text-xs text-zinc-500 uppercase tracking-wide">{label}</p>
      <p className={`text-lg font-semibold mt-1 ${accent}`}>{value}</p>
    </div>
  );
}
