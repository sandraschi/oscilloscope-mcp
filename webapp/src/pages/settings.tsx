import { useQuery } from "@tanstack/react-query";
import { getCapabilities, getStatus } from "@/lib/api";

export default function Settings() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus });
  const { data: caps } = useQuery({ queryKey: ["capabilities"], queryFn: getCapabilities });

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 space-y-4">
        <Row label="Capture directory" value={status?.capture_dir ?? "-"} />
        <Row label="Active backend" value={status?.active_backend ?? "auto"} />
        <Row label="Backend port" value="10936" />
        <Row label="Frontend port" value="10937" />
        <Row label="MCP endpoint" value="http://127.0.0.1:10936/mcp" />
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mt-6">
        <h2 className="text-lg font-semibold mb-3">Capabilities</h2>
        <pre className="text-xs text-zinc-300 overflow-x-auto">{JSON.stringify(caps, null, 2)}</pre>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 text-sm border-b border-zinc-800 pb-2">
      <span className="text-zinc-500">{label}</span>
      <span className="font-mono text-zinc-200">{value}</span>
    </div>
  );
}
