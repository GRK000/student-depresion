import { Navigate, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Lock, Shield, TimerReset } from "lucide-react";

import ChatInput from "../components/chat/ChatInput";
import ChatWindow from "../components/chat/ChatWindow";
import ProgressHeader from "../components/chat/ProgressHeader";
import Card from "../components/ui/Card";
import SafetyBanner from "../components/ui/SafetyBanner";
import { useAssessmentState } from "../hooks/useAssessmentState.jsx";
import { useChatFlow } from "../hooks/useChatFlow";

function Assessment() {
  const navigate = useNavigate();
  const { hasAcceptedDisclaimer, exitAssessment, restartAssessment } = useAssessmentState();
  const { messages, progress, currentQuestion, isTyping, isSubmitting, submitAnswer } = useChatFlow();

  if (!hasAcceptedDisclaimer) {
    return <Navigate to="/" replace />;
  }

  const handleExit = () => {
    exitAssessment();
    navigate("/");
  };

  const handleRestart = () => {
    restartAssessment();
    navigate("/assessment", { replace: true });
  };

  return (
    <main className="relative z-10 mx-auto min-h-screen w-full max-w-7xl px-4 pb-8 pt-5 sm:px-6 lg:px-8">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,760px)_280px] lg:items-start">
        <section className="min-h-[calc(100vh-3rem)]">
          <ProgressHeader progress={progress} onExit={handleExit} onRestart={handleRestart} />

          <Card className="mt-5 flex min-h-[calc(100vh-9rem)] flex-col overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/80 px-5 py-4">
              <SafetyBanner />
              <p className="text-sm text-muted">
                Conversación guiada y lenguaje claro para recoger información relevante.
              </p>
            </div>

            <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-3 py-5 sm:px-5">
              <ChatWindow messages={messages} isTyping={isTyping || isSubmitting} />
            </div>

            <ChatInput
              suggestions={currentQuestion?.suggestions ?? []}
              disabled={isTyping || isSubmitting}
              onSubmit={submitAnswer}
            />
          </Card>
        </section>

        <aside className="hidden lg:block">
          <div className="sticky top-5 space-y-4">
            <Card className="p-5">
              <div className="mb-3 inline-flex rounded-2xl bg-primary/10 p-3 text-primary">
                <Shield size={18} />
              </div>
              <h2 className="text-lg font-semibold text-ink">Privacidad y límites</h2>
              <p className="mt-2 text-sm leading-7 text-muted">
                Esta experiencia está diseñada para orientar, no para etiquetar ni sustituir ayuda profesional.
              </p>
            </Card>

            <Card className="p-5">
              <div className="mb-3 inline-flex rounded-2xl bg-secondary/16 p-3 text-emerald-700">
                <Lock size={18} />
              </div>
              <h2 className="text-lg font-semibold text-ink">Ritmo amable</h2>
              <p className="mt-2 text-sm leading-7 text-muted">
                El progreso se expresa como información recopilada para que la conversación suene menos rígida.
              </p>
            </Card>

            <Card className="p-5">
              <div className="mb-3 inline-flex rounded-2xl bg-warning/18 p-3 text-amber-700">
                <TimerReset size={18} />
              </div>
              <h2 className="text-lg font-semibold text-ink">Puedes reiniciar</h2>
              <p className="mt-2 text-sm leading-7 text-muted">
                Si quieres empezar de nuevo, el botón de reinicio limpia la conversación actual.
              </p>
            </Card>
          </div>
        </aside>
      </div>

      <AnimatePresence>
        {isSubmitting ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/10 backdrop-blur-sm"
          >
            <Card className="w-full max-w-md p-6 text-center">
              <p className="text-sm font-medium text-primary">Preparando resultado</p>
              <h2 className="mt-2 text-2xl font-semibold text-ink">Un momento</h2>
              <p className="mt-3 text-sm leading-7 text-muted">
                Estoy ordenando la información recogida para devolverte una orientación clara y responsable.
              </p>
            </Card>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </main>
  );
}

export default Assessment;
