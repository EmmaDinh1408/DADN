import { Cog, Link2, Settings2, Bot, Sparkles, FileText, History, LogOut, FolderKanban, Lock, Check } from "lucide-react";
import { GearLogo } from "./GearLogo";
import { useWorkflow, PIPELINE } from "./workflow";

export type ModuleKey =
  | "projects"
  | "optimizer"
  | "motor"
  | "chain"
  | "gearbox"
  | "report"
  | "chatbot"
  | "history";

const meta: Record<ModuleKey, { label: string; icon: any }> = {
  projects:  { label: "Dự án",        icon: FolderKanban },
  optimizer: { label: "AI Optimizer", icon: Sparkles },
  motor:     { label: "Động cơ",      icon: Cog },
  chain:     { label: "Xích",         icon: Link2 },
  gearbox:   { label: "Bánh răng",    icon: Settings2 },
  report:    { label: "Báo cáo",      icon: FileText },
  chatbot:   { label: "Chatbot",      icon: Bot },
  history:   { label: "Lịch sử",      icon: History },
};

const utility: ModuleKey[] = ["chatbot", "history"];

export function Sidebar({
  active,
  onChange,
  onLogout,
  user,
}: {
  active: ModuleKey;
  onChange: (k: ModuleKey) => void;
  onLogout?: () => void;
  user?: { name: string; email: string };
}) {
  const { done, isUnlocked } = useWorkflow();

  return (
    <aside className="w-64 shrink-0 h-full bg-white border-r border-stone-200 flex flex-col">
      <div className="px-5 pt-6 pb-4 flex items-center gap-2.5">
        <GearLogo size={28} />
        <p className="text-stone-900" style={{ fontSize: 14, letterSpacing: '0.05em' }}>MechDrive</p>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-2">
        <GroupLabel>Quy trình</GroupLabel>
        {PIPELINE.map((key, i) => {
          const m = meta[key];
          const unlocked = isUnlocked(key);
          const isDone = done.has(key);
          const on = active === key;
          return (
            <StepRow
              key={key}
              index={i + 1}
              label={m.label}
              icon={m.icon}
              active={on}
              done={isDone}
              locked={!unlocked}
              onClick={() => unlocked && onChange(key)}
            />
          );
        })}

        <GroupLabel>Tiện ích</GroupLabel>
        {utility.map((key) => {
          const m = meta[key];
          const on = active === key;
          const Icon = m.icon;
          return (
            <button
              key={key}
              onClick={() => onChange(key)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all ${
                on
                  ? "bg-gradient-to-r from-yellow-100/80 to-pink-100/80 text-stone-800"
                  : "hover:bg-stone-50 text-stone-700"
              }`}
            >
              <Icon size={15} className={on ? "text-stone-700" : "text-stone-400"} />
              <span className="truncate" style={{ fontSize: 13 }}>{m.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-stone-200 p-3">
        {user && (
          <div className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-yellow-300 to-pink-300 text-stone-800 flex items-center justify-center" style={{ fontSize: 12 }}>
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0 truncate text-stone-700" style={{ fontSize: 13 }}>{user.name}</div>
            {onLogout && (
              <button onClick={onLogout} className="p-1.5 rounded-md text-stone-400 hover:bg-stone-100 hover:text-stone-600">
                <LogOut size={14} />
              </button>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}

function GroupLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-3 pt-3 pb-1.5 text-stone-400 uppercase tracking-wider" style={{ fontSize: 11 }}>
      {children}
    </div>
  );
}

function StepRow({
  index,
  label,
  icon: Icon,
  active,
  done,
  locked,
  onClick,
}: {
  index: number;
  label: string;
  icon: any;
  active: boolean;
  done: boolean;
  locked: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={locked}
      className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all ${
        active
          ? "bg-gradient-to-r from-yellow-100/80 to-pink-100/80 text-stone-800"
          : locked
          ? "text-stone-300 cursor-not-allowed"
          : "hover:bg-stone-50 text-stone-700"
      }`}
    >
      <span
        className={`w-6 h-6 rounded-full inline-flex items-center justify-center shrink-0 ${
          done
            ? "bg-gradient-to-br from-yellow-200 to-pink-300 text-stone-800"
            : active
            ? "bg-white border border-pink-200 text-stone-800"
            : locked
            ? "bg-stone-100 text-stone-300"
            : "bg-stone-100 text-stone-500"
        }`}
        style={{ fontSize: 11 }}
      >
        {done ? <Check size={12} /> : locked ? <Lock size={11} /> : index}
      </span>
      <Icon size={14} className={locked ? "text-stone-300" : active ? "text-stone-700" : "text-stone-400"} />
      <span className="truncate" style={{ fontSize: 13 }}>{label}</span>
    </button>
  );
}
