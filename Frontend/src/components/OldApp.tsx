"use client";
import { useState, useEffect } from "react";
import { Sidebar, ModuleKey } from "./Sidebar";
import { ModuleMotor } from "./ModuleMotor";
import { ModuleChain } from "./ModuleChain";
import { ModuleGearbox } from "./ModuleGearbox";
import { ModuleOptimizer } from "./ModuleOptimizer";
import { Chatbot } from "./Chatbot";
import { ReportPanel } from "./ReportPanel";
import { HistoryPage } from "./HistoryPage";
import { AuthScreen } from "./AuthScreen";
import { ModuleProjects } from "./ModuleProjects";
import { WorkflowProvider } from "./workflow";
import { createClient } from "@/utils/supabase/client";

export default function App() {
  const [user, setUser] = useState<{ id: string; name: string; email: string } | null>(null);
  const [active, setActive] = useState<ModuleKey>("projects");
  const [currentScheme, setCurrentScheme] = useState<{ projectID: number; schemeNo: number } | null>(null);
  const [aiResult, setAiResult] = useState<any>(null);
  const supabase = createClient();

  useEffect(() => {
  }, []);

  const handleLogout = async () => {
    setUser(null);
  };

  if (!user) return <AuthScreen onAuth={setUser} />;

  return (
    <WorkflowProvider>
      <div className="size-full flex bg-white">
        <Sidebar active={active} onChange={setActive} user={user} onLogout={handleLogout} />
        <main className="flex-1 flex flex-col overflow-hidden">
          {active === "projects" && <ModuleProjects onGoto={setActive} user={user} onSetScheme={setCurrentScheme} />}
          {active === "optimizer" && <ModuleOptimizer onGoto={setActive} onSuccess={setAiResult} currentScheme={currentScheme} />}
          {active === "motor" && <ModuleMotor onGoto={setActive} aiResult={aiResult} currentScheme={currentScheme} />}
          {active === "chain" && <ModuleChain onGoto={setActive} aiResult={aiResult} />}
          {active === "gearbox" && <ModuleGearbox onGoto={setActive} aiResult={aiResult} currentScheme={currentScheme} />}
          {active === "report" && <ReportPanel user={user} currentScheme={currentScheme} onGoto={setActive} />}
          {active === "chatbot" && <Chatbot />}
          {active === "history" && <HistoryPage user={user} />}
        </main>
      </div>
    </WorkflowProvider>
  );
}
