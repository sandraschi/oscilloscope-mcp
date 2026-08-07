import { NavLink } from "react-router-dom";
import {
  Activity,
  Cable,
  HelpCircle,
  LayoutDashboard,
  List,
  Settings,
  SlidersHorizontal,
  Waves,
  Wrench,
  Zap,
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/device", label: "Device", icon: Cable },
  { to: "/waveform", label: "Waveform", icon: Waves },
  { to: "/configure", label: "Configure", icon: SlidersHorizontal },
  { to: "/trigger", label: "Trigger", icon: Zap },
  { to: "/tools", label: "Tools", icon: Wrench },
  { to: "/logs", label: "Logs", icon: List },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/help", label: "Help", icon: HelpCircle },
];

export default function Sidebar() {
  return (
    <aside className="w-56 border-r border-zinc-800 bg-zinc-900/80 backdrop-blur p-4 flex flex-col gap-2">
      <div className="flex items-center gap-2 mb-4 px-2">
        <Activity className="text-amber-400" size={20} />
        <div>
          <p className="font-semibold text-sm">Oscilloscope</p>
          <p className="text-xs text-zinc-500">MCP v0.1.0</p>
        </div>
      </div>
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition ${
              isActive ? "bg-amber-500/20 text-amber-300" : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
            }`
          }
        >
          <Icon size={16} />
          {label}
        </NavLink>
      ))}
    </aside>
  );
}
