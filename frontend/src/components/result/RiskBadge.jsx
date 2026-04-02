function toneClasses(level) {
  if (level === "Alto") {
    return "bg-danger/12 text-danger";
  }
  if (level === "Moderado") {
    return "bg-warning/18 text-amber-700";
  }
  return "bg-success/16 text-emerald-700";
}

function RiskBadge({ label }) {
  return (
    <span className={`inline-flex rounded-full px-4 py-2 text-sm font-semibold ${toneClasses(label)}`}>
      Riesgo estimado: {label}
    </span>
  );
}

export default RiskBadge;
