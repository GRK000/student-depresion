import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Lock, MessagesSquare, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import BrandMark from "../components/ui/BrandMark";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Modal from "../components/ui/Modal";
import { useAssessmentState } from "../hooks/useAssessmentState.jsx";

function Home() {
  const navigate = useNavigate();
  const { startAssessment } = useAssessmentState();
  const [showModal, setShowModal] = useState(false);
  const [accepted, setAccepted] = useState(false);

  const beginAssessment = () => {
    if (!accepted) {
      return;
    }

    startAssessment();
    navigate("/assessment");
  };

  return (
    <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 pb-12 pt-6 sm:px-8 lg:px-10">
      <header className="flex items-center justify-between py-4">
        <BrandMark />
        <Button as={Link} to="/about" variant="ghost">
          Saber cómo funciona
        </Button>
      </header>

      <section className="grid flex-1 items-center gap-10 py-8 lg:grid-cols-[1.2fr_0.8fr] lg:py-14">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className="max-w-3xl"
        >
          <div className="mb-6 inline-flex rounded-full border border-primary/15 bg-white/75 px-4 py-2 text-sm text-muted shadow-soft backdrop-blur">
            Herramienta orientativa · Basada en datos · No sustituye ayuda profesional
          </div>
          <h1 className="max-w-3xl font-display text-4xl font-semibold leading-tight text-ink sm:text-5xl lg:text-6xl">
            Conversación guiada para evaluar indicadores de bienestar emocional
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-9 text-muted">
            Esta herramienta no sustituye a un profesional de la salud mental. Su objetivo es orientarte mediante una conversación estructurada y una predicción basada en datos.
          </p>

          <div className="mt-10 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" onClick={() => setShowModal(true)}>
              Comenzar conversación
              <ArrowRight size={18} />
            </Button>
            <Button as={Link} to="/about" size="lg" variant="secondary">
              Saber cómo funciona
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.08, ease: "easeOut" }}
        >
          <Card className="grid-fade overflow-hidden p-7 sm:p-8">
            <div className="rounded-[26px] border border-white/70 bg-white/90 p-5 shadow-soft">
              <p className="text-sm font-medium text-primary">Vista previa</p>
              <div className="mt-4 space-y-4">
                <div className="rounded-[22px] border border-border bg-white p-4 text-sm leading-7 text-ink">
                  Gracias por estar aquí. Vamos paso a paso. ¿Cómo describirías tus últimos días?
                </div>
                <div className="ml-auto max-w-xs rounded-[22px] rounded-br-md bg-user-bubble px-4 py-3 text-sm leading-7 text-ink">
                  He estado bastante agobiado con la universidad.
                </div>
                <div className="rounded-[22px] border border-border bg-white p-4 text-sm leading-7 text-ink">
                  Gracias por compartirlo. ¿Dirías que ese agobio está afectando a tu sueño?
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {[
          {
            icon: MessagesSquare,
            title: "Conversación guiada",
            description: "Un recorrido paso a paso para recoger señales relevantes sin que la experiencia se sienta rígida.",
          },
          {
            icon: Sparkles,
            title: "Predicción explicable",
            description: "El resultado se acompaña de factores influyentes y una explicación en lenguaje claro.",
          },
          {
            icon: Lock,
            title: "Privacidad y límites",
            description: "La app comunica con claridad qué hace, qué no hace y por qué el resultado es solo orientativo.",
          },
        ].map((item) => (
          <Card key={item.title} className="p-6">
            <div className="mb-4 inline-flex rounded-2xl bg-primary/10 p-3 text-primary">
              <item.icon size={20} />
            </div>
            <h2 className="text-xl font-semibold text-ink">{item.title}</h2>
            <p className="mt-3 text-sm leading-7 text-muted">{item.description}</p>
          </Card>
        ))}
      </section>

      <Modal
        open={showModal}
        title="Confirmación breve antes de empezar"
        onClose={() => setShowModal(false)}
        footer={
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <label className="flex items-start gap-3 rounded-2xl border border-border bg-slate-50 px-4 py-3 text-sm text-muted">
              <input
                type="checkbox"
                checked={accepted}
                onChange={(event) => setAccepted(event.target.checked)}
                className="mt-1 h-4 w-4 rounded border-border text-primary focus:ring-primary"
              />
              <span>He leído que la herramienta es orientativa y no sustituye apoyo profesional.</span>
            </label>
            <Button onClick={beginAssessment} disabled={!accepted}>
              Continuar
            </Button>
          </div>
        }
      >
        <p>Esta herramienta ofrece una orientación basada en datos y una conversación guiada.</p>
        <p>No sustituye a un profesional de la salud mental ni emite un diagnóstico clínico.</p>
        <p>Si lo que sientes te preocupa o afecta a tu seguridad, busca apoyo profesional cuanto antes.</p>
      </Modal>
    </main>
  );
}

export default Home;
