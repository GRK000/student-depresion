import { ArrowRight, RefreshCw, MessageCircleMore } from "lucide-react";
import { Link } from "react-router-dom";

import Button from "../ui/Button";
import Card from "../ui/Card";

function RecommendationPanel({ recommendations, modelVersion, onRestart }) {
  return (
    <Card className="p-6 sm:p-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-medium text-primary">Recomendaciones responsables</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Próximos pasos con calma</h2>
        </div>
        <p className="text-sm text-muted">Modelo usado: {modelVersion}</p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {recommendations.map((item) => (
          <div
            key={item}
            className="rounded-[24px] border border-border bg-slate-50/80 p-5 text-sm leading-7 text-muted"
          >
            {item}
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <Button onClick={onRestart}>
          <MessageCircleMore size={16} />
          Volver a conversar
        </Button>
        <Button variant="secondary" onClick={onRestart}>
          <RefreshCw size={16} />
          Nueva evaluación
        </Button>
        <Button as={Link} to="/about" variant="ghost" className="sm:ml-auto">
          Ver cómo funciona
          <ArrowRight size={16} />
        </Button>
      </div>
    </Card>
  );
}

export default RecommendationPanel;
