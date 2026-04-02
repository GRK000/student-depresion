import { Navigate, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Info } from "lucide-react";

import FactorCard from "../components/result/FactorCard";
import RecommendationPanel from "../components/result/RecommendationPanel";
import ResultSummary from "../components/result/ResultSummary";
import BrandMark from "../components/ui/BrandMark";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import { useAssessmentState } from "../hooks/useAssessmentState.jsx";

function Results() {
  const navigate = useNavigate();
  const { result, restartAssessment } = useAssessmentState();

  if (!result) {
    return <Navigate to="/" replace />;
  }

  const handleRestart = () => {
    restartAssessment();
    navigate("/assessment");
  };

  return (
    <main className="relative z-10 mx-auto min-h-screen w-full max-w-6xl px-4 pb-10 pt-6 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <BrandMark compact />
        <Button variant="ghost" onClick={() => navigate("/assessment")}>
          <ArrowLeft size={16} />
          Volver al chat
        </Button>
      </div>

      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        >
          <ResultSummary result={result} />
        </motion.div>

        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05, ease: "easeOut" }}
          className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]"
        >
          <Card className="p-6 sm:p-8">
            <p className="text-sm font-medium text-primary">Explicación clara</p>
            <h2 className="mt-2 text-2xl font-semibold text-ink">Qué está pesando más en el resultado</h2>
            <p className="mt-4 text-base leading-8 text-muted">{result.explanation}</p>

            <div className="mt-6 flex items-start gap-3 rounded-[24px] border border-border bg-slate-50/80 p-4">
              <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                <Info size={18} />
              </div>
              <p className="text-sm leading-7 text-muted">
                La explicación se presenta en lenguaje sencillo para que se entienda el resultado sin jerga técnica.
              </p>
            </div>
          </Card>

          <div className="grid gap-4">
            {result.factors.map((factor) => (
              <FactorCard key={factor.title} factor={factor} />
            ))}
          </div>
        </motion.section>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.08, ease: "easeOut" }}
        >
          <RecommendationPanel
            recommendations={result.recommendations}
            modelVersion={result.modelVersion}
            onRestart={handleRestart}
          />
        </motion.div>
      </div>
    </main>
  );
}

export default Results;
