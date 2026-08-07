import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/dashboard";
import DevicePage from "@/pages/device";
import Waveform from "@/pages/waveform";
import ConfigurePage from "@/pages/configure";
import TriggerPage from "@/pages/trigger";
import Logs from "@/pages/logs";
import ToolsPage from "@/pages/tools";
import Settings from "@/pages/settings";
import Help from "@/pages/help";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/device" element={<DevicePage />} />
        <Route path="/waveform" element={<Waveform />} />
        <Route path="/configure" element={<ConfigurePage />} />
        <Route path="/trigger" element={<TriggerPage />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
