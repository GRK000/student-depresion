import { ShieldCheck } from "lucide-react";

function SafetyBanner({ className = "" }) {
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border border-primary/14 bg-primary/6 px-3.5 py-2 text-sm text-muted ${className}`}
    >
      <ShieldCheck size={16} className="text-primary" />
      <span>Herramienta orientativa. No ofrece diagnóstico clínico.</span>
    </div>
  );
}

export default SafetyBanner;
