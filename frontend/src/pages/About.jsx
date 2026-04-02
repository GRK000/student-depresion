import { motion } from "framer-motion";
import { Database, Lock, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import BrandMark from "../components/ui/BrandMark";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

function About() {
  const sections = [
    {
      icon: Database,
      title: "Qué datos recoge",
      body: "La conversación está pensada para completar las variables que usa el modelo actual: edad, presión académica, horas de sueño, estrés financiero, satisfacción con estudios o trabajo, hábitos y algunos antecedentes relevantes.",
    },
    {
      icon: Sparkles,
      title: "Cómo se usa el modelo",
      body: "La interfaz traduce la conversación a un conjunto estructurado de variables y solicita una predicción al backend. Después genera una explicación breve y humana a partir de los factores más influyentes detectados.",
    },
    {
      icon: ShieldCheck,
      title: "Qué limitaciones tiene",
      body: "No reemplaza una evaluación profesional, no emite un diagnóstico clínico y depende de la calidad de la información compartida. Su función es orientar y ayudar a ordenar señales, no decidir por una persona.",
    },
    {
      icon: Lock,
      title: "Privacidad y responsabilidad",
      body: "La app comunica de forma explícita que el resultado es orientativo. Si alguien siente que su seguridad podría estar en riesgo o el malestar es intenso, la recomendación responsable es buscar apoyo profesional inmediato.",
    },
  ];

  return (
    <main className="relative z-10 mx-auto min-h-screen w-full max-w-6xl px-4 pb-12 pt-6 sm:px-6 lg:px-8">
      <header className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <BrandMark />
        <div className="flex gap-3">
          <Button as={Link} to="/" variant="secondary">
            Volver
          </Button>
          <Button as={Link} to="/">
            Comenzar desde inicio
          </Button>
        </div>
      </header>

      <motion.section
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="mt-12 max-w-4xl"
      >
        <p className="text-sm font-medium text-primary">Cómo funciona</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
          Una interfaz calmada para una evaluación orientativa y explicable
        </h1>
        <p className="mt-6 text-lg leading-9 text-muted">
          El objetivo no es dramatizar ni aparentar una consulta clínica. La experiencia está diseñada para recoger información con orden, devolver una señal comprensible y dejar claros sus límites.
        </p>
      </motion.section>

      <section className="mt-10 grid gap-5 md:grid-cols-2">
        {sections.map((section, index) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.05 * index, ease: "easeOut" }}
          >
            <Card className="h-full p-6">
              <div className="mb-4 inline-flex rounded-2xl bg-primary/10 p-3 text-primary">
                <section.icon size={20} />
              </div>
              <h2 className="text-xl font-semibold text-ink">{section.title}</h2>
              <p className="mt-3 text-sm leading-7 text-muted">{section.body}</p>
            </Card>
          </motion.div>
        ))}
      </section>
    </main>
  );
}

export default About;
