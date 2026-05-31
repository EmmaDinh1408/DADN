export function GearLogo({ size = 32 }: { size?: number }) {
  return (
    <span
      className="gear-logo inline-flex shrink-0"
      style={{ width: size, height: size }}
      aria-hidden
    >
      <svg viewBox="0 0 64 64" width={size} height={size} className="gear-logo-svg block">
        <defs>
          <linearGradient id="gear-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fde68a" />
            <stop offset="50%" stopColor="#fbcfe8" />
            <stop offset="100%" stopColor="#f9a8d4" />
          </linearGradient>
        </defs>
        <g
          fill="none"
          stroke="url(#gear-grad)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {}
          {Array.from({ length: 8 }).map((_, i) => {
            const a = (i * Math.PI * 2) / 8;
            const r1 = 22;
            const r2 = 29;
            const x1 = 32 + Math.cos(a) * r1;
            const y1 = 32 + Math.sin(a) * r1;
            const x2 = 32 + Math.cos(a) * r2;
            const y2 = 32 + Math.sin(a) * r2;
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} />;
          })}
          {}
          <circle cx="32" cy="32" r="20" />
          {}
          <circle cx="32" cy="32" r="7" />
        </g>
      </svg>
    </span>
  );
}
