import { Button, Badge } from "./ui-bits";
import { Check, ArrowRight, Save, RotateCcw, Lollipop } from "lucide-react";
import { useWorkflow } from "./workflow";
import type { ModuleKey } from "./Sidebar";

function IconBtn({ icon: Icon, label, onClick, variant, disabled, title: titleProp }: {
  icon: any; label: string; onClick?: () => void; variant?: "outline" | "ghost"; disabled?: boolean; title?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={titleProp || label}
      className={`group relative p-2.5 rounded-xl transition-all ${
        disabled ? "opacity-40 cursor-not-allowed" :
        variant === "outline"
          ? "border border-stone-200 text-stone-600 hover:bg-stone-50 hover:text-stone-900 hover:border-stone-300"
          : variant === "ghost"
          ? "text-stone-500 hover:bg-stone-100 hover:text-stone-800"
          : "bg-gradient-to-r from-yellow-200 to-pink-200 text-stone-800 shadow-sm hover:shadow-md"
      }`}
    >
      <Icon size={16} />
      <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded-lg bg-stone-800 text-white text-[11px] opacity-0 group-hover:opacity-100 transition-opacity shadow-lg z-50">
        {label}
      </span>
    </button>
  );
}

export function Header({
  title,
  desc,
  onRun,
  stepKey,
  onGoto,
  runDisabled,
  runDisabledHint,
  saving,
}: {
  title: string;
  desc?: string;
  onRun?: () => void;
  stepKey?: ModuleKey;
  onGoto?: (k: ModuleKey) => void;
  runDisabled?: boolean;
  runDisabledHint?: string;
  saving?: boolean;
}) {
  const { done, markDone, nextOf } = useWorkflow();
  const isDone = stepKey ? done.has(stepKey) : false;
  const next = stepKey ? nextOf(stepKey) : null;

  const handleRun = () => {
    onRun?.();
    if (stepKey) markDone(stepKey);
  };

  return (
    <header className="flex items-center justify-between gap-4 px-8 py-4 border-b border-stone-200 bg-white/95 backdrop-blur">
      <div className="min-w-0 flex items-center gap-3">
        <div className="min-w-0">
          <h1 className="text-stone-900 font-bold truncate" style={{ fontSize: 17, letterSpacing: '0.03em' }}>{title}</h1>
          {desc && <p className="text-stone-400 mt-0.5 truncate" style={{ fontSize: 11 }}>{desc}</p>}
        </div>
        {isDone && <Badge tone="green">Hoàn thành</Badge>}
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        <IconBtn icon={Save} label="Lưu" variant="outline" />

        {onRun && (
          <button
            onClick={handleRun}
            disabled={runDisabled || saving}
            title={runDisabled ? runDisabledHint : isDone ? "Tính lại" : "Tính & hoàn thành"}
            className={`group relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
              runDisabled || saving
                ? "opacity-40 cursor-not-allowed bg-stone-200 text-stone-500"
                : "bg-gradient-to-r from-yellow-200 to-pink-300 text-stone-800 shadow-sm hover:shadow-md"
            }`}
          >
            {saving ? (
              <><Lollipop size={14} className="animate-spin" /> Đang lưu...</>
            ) : (
              <>
                {isDone ? <RotateCcw size={14} /> : <Check size={14} />}
                <span className="hidden sm:inline">{isDone ? "Tính lại" : "Tính & hoàn thành"}</span>
              </>
            )}
          </button>
        )}

        {isDone && next && onGoto && (
          <IconBtn icon={ArrowRight} label="Bước tiếp theo" variant="outline" onClick={() => onGoto(next)} />
        )}
      </div>
    </header>
  );
}
