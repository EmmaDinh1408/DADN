"use client";
import { createContext, useContext, useMemo, useState, ReactNode } from "react";
import type { ModuleKey } from "./Sidebar";

export const PIPELINE: ModuleKey[] = ["projects", "optimizer", "motor", "chain", "gearbox", "report"];

export const STEP_LABEL: Record<ModuleKey, string> = {
  projects:  "Dự án",
  optimizer: "AI Optimizer",
  motor:     "Động cơ",
  chain:     "Xích",
  gearbox:   "Bánh răng",
  report:    "Báo cáo",
  chatbot:   "Chatbot",
  history:   "Lịch sử",
};

type Ctx = {
  done: Set<ModuleKey>;
  markDone: (k: ModuleKey) => void;
  reset: () => void;
  isUnlocked: (k: ModuleKey) => boolean;
  nextOf: (k: ModuleKey) => ModuleKey | null;
};

const WorkflowCtx = createContext<Ctx | null>(null);

export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [done, setDone] = useState<Set<ModuleKey>>(new Set());

  const value = useMemo<Ctx>(() => {
    const isUnlocked = (k: ModuleKey) => {
      if (k === "chatbot" || k === "history") return true;
      const i = PIPELINE.indexOf(k);
      if (i <= 0) return true;
      return done.has(PIPELINE[i - 1]);
    };
    const nextOf = (k: ModuleKey) => {
      const i = PIPELINE.indexOf(k);
      if (i < 0 || i >= PIPELINE.length - 1) return null;
      return PIPELINE[i + 1];
    };
    return {
      done,
      markDone: (k) => setDone((prev) => new Set(prev).add(k)),
      reset: () => setDone(new Set()),
      isUnlocked,
      nextOf,
    };
  }, [done]);

  return <WorkflowCtx.Provider value={value}>{children}</WorkflowCtx.Provider>;
}

export function useWorkflow() {
  const c = useContext(WorkflowCtx);
  if (!c) throw new Error("useWorkflow must be inside WorkflowProvider");
  return c;
}
