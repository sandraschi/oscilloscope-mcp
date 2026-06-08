import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import Dashboard from "@/pages/dashboard";
import Waveform from "@/pages/waveform";
import ToolsPage from "@/pages/tools";
import Settings from "@/pages/settings";
import Help from "@/pages/help";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/waveform" element={<Waveform />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
