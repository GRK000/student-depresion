import Card from "../ui/Card";
import RiskBadge from "./RiskBadge";

function ResultSummary({ result }) {
  const width = `${Math.round(result.probability * 100)}%`;

  return (
    <Card className="p-6 sm:p-8">
      <p className="text-sm font-medium text-primary">Resultado de la evaluación</p>
      <div className="mt-3 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <h1 className="text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Una orientación clara y prudente
          </h1>
          <p className="mt-3 text-base leading-8 text-muted">{result.summary}</p>
        </div>
        <RiskBadge label={result.riskLevel.label} />
      </div>

      <div className="mt-8 rounded-[24px] border border-border bg-slate-50/80 p-5">
        <div className="mb-3 flex items-center justify-between text-sm">
          <span className="font-medium text-ink">Señal estimada</span>
          <span className="text-muted">{Math.round(result.probability * 100)}%</span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-white">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              result.riskLevel.label === "Alto"
                ? "bg-danger"
                : result.riskLevel.label === "Moderado"
                  ? "bg-warning"
                  : "bg-success"
            }`}
            style={{ width }}
          />
        </div>
        <p className="mt-4 text-sm leading-7 text-muted">
          Este resultado no es un diagnóstico clínico. Resume una combinación de señales recogidas en la conversación.
        </p>
      </div>
    </Card>
  );
}

export default ResultSummary;
