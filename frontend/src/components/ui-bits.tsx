import { ReactNode } from "react";

export function Card({ title, children, accent, action }: { title?: string| React.ReactNode; children: ReactNode; accent?: boolean; action?: ReactNode }) {
  return (
    <div
      className={`pop-in rounded-2xl p-6 border ${
        accent
          ? "bg-gradient-to-br from-yellow-50 via-white to-pink-50 border-pink-200 shadow-sm"
          : "bg-white border-stone-200"
      }`}
    >
      {(title || action) && (
        <div className="flex items-center justify-between mb-4 gap-3">
          {title && <div className="text-stone-800 truncate" style={{ fontSize: 14, letterSpacing: '0.04em' }}>{title}</div>}
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

const controlBase =
  "w-full h-11 px-3 rounded-xl bg-white border border-stone-200 focus:border-pink-300 focus:ring-2 focus:ring-pink-100 outline-none transition text-stone-800";

export function Field({
  label,
  unit,
  value,
  onChange,
  type = "number",
  placeholder,
  error,
}: {
  label?: string;
  unit?: string;
  value: string | number;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  error?: string;
}) {
  return (
    <label className="block">
      {label && (
        <div className="flex justify-between items-baseline mb-1.5">
          <span className="text-stone-600 truncate" style={{ fontSize: 12 }}>{label}</span>
          {unit && <span className="text-stone-400" style={{ fontSize: 11 }}>{unit}</span>}
        </div>
      )}
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className={controlBase + (error ? " border-pink-400 focus:border-pink-500 focus:ring-pink-200" : "")}
        style={{ fontSize: 14 }}
      />
      {error && (
        <div className="mt-1 text-pink-600" style={{ fontSize: 11 }}>{error}</div>
      )}
    </label>
  );
}

export function Select({
  label,
  value,
  onChange,
  options,
}: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="block">
      {label && <div className="mb-1.5 text-stone-600" style={{ fontSize: 12 }}>{label}</div>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={controlBase + " appearance-none pr-8"}
        style={{
          fontSize: 14,
          backgroundImage:
            "url(\"data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a8a29e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E\")",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "right 12px center",
        }}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}

export function Result({ label, value, unit, hi }: { label: string; value: string | number; unit?: string; hi?: boolean }) {
  return (
    <div
      className={`flex items-baseline justify-between py-2 px-3 rounded-lg ${
        hi ? "bg-gradient-to-r from-yellow-100/70 to-pink-100/70" : ""
      }`}
    >
      <span className="text-stone-600 truncate" style={{ fontSize: 13 }}>{label}</span>
      <span className="text-stone-900 font-mono shrink-0 ml-3" style={{ fontSize: 13 }}>
        {value} {unit && <span className="text-stone-400">{unit}</span>}
      </span>
    </div>
  );
}

export function Badge({ children, tone = "rose" }: { children: ReactNode; tone?: "rose" | "amber" | "green" | "stone" }) {
  const tones = {
    rose: "bg-pink-100 text-stone-700",
    amber: "bg-yellow-100 text-stone-800",
    green: "bg-green-100 text-green-700",
    stone: "bg-stone-100 text-stone-600",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full ${tones[tone]}`} style={{ fontSize: 11, letterSpacing: '0.03em' }}>
      {children}
    </span>
  );
}

export function Button({
  children,
  onClick,
  variant = "primary",
  size = "md",
  type = "button",
  disabled,
  title,
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "ghost" | "outline";
  size?: "sm" | "md";
  type?: "button" | "submit";
  disabled?: boolean;
  title?: string;
}) {
  const sizes = { sm: "h-9 px-3", md: "h-11 px-5" };
  const variants = {
    primary: "bg-gradient-to-r from-yellow-200 to-pink-300 border border-pink-300/60 text-stone-800 shadow-sm hover:shadow-md",
    ghost: "text-stone-600 border border-transparent hover:border-stone-200 hover:bg-stone-50",
    outline: "bg-white border border-stone-300 text-stone-700 hover:bg-stone-50 hover:border-stone-400",
  };
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`inline-flex items-center justify-center gap-2 rounded-lg ${sizes[size]} ${variants[variant]} ${disabled ? "opacity-40 cursor-not-allowed pointer-events-none" : ""}`}
      style={{ fontSize: 13 }}
    >
      {children}
    </button>
  );
}
