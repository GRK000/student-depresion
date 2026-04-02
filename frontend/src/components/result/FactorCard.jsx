import { Moon, Wallet, GraduationCap, ShieldAlert, Sparkles } from "lucide-react";

import Card from "../ui/Card";

function getIcon(title) {
  if (title.toLowerCase().includes("sueño")) {
    return Moon;
  }
  if (title.toLowerCase().includes("financ")) {
    return Wallet;
  }
  if (title.toLowerCase().includes("acad")) {
    return GraduationCap;
  }
  if (title.toLowerCase().includes("alarma")) {
    return ShieldAlert;
  }
  return Sparkles;
}

function getToneClasses(tone) {
  if (tone === "high") {
    return "bg-danger/10 text-danger";
  }
  if (tone === "medium") {
    return "bg-warning/18 text-amber-700";
  }
  return "bg-success/16 text-emerald-700";
}

function FactorCard({ factor }) {
  const Icon = getIcon(factor.title);

  return (
    <Card className="p-5">
      <div className={`mb-4 inline-flex rounded-2xl p-3 ${getToneClasses(factor.tone)}`}>
        <Icon size={20} />
      </div>
      <h3 className="text-lg font-semibold text-ink">{factor.title}</h3>
      <p className="mt-2 text-sm leading-7 text-muted">{factor.description}</p>
    </Card>
  );
}

export default FactorCard;
