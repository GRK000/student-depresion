import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAssessmentState } from "./useAssessmentState.jsx";
import { predictAssessment } from "../services/api";

const QUESTIONS = [
  {
    field: "age",
    prompt: "Para situar mejor la conversación, ¿qué edad tienes?",
    help: "Puedes responder con un número entre 18 y 60.",
    suggestions: ["18", "21", "25"],
    parse(value) {
      const number = Number.parseFloat(value.replace(",", "."));
      if (Number.isNaN(number) || number < 18 || number > 60) {
        return { ok: false, error: "Necesito una edad válida entre 18 y 60 años." };
      }
      return { ok: true, value: number };
    },
  },
  {
    field: "gender",
    prompt: "¿Con qué género te identificas dentro de las opciones que usa el modelo?",
    help: "Actualmente el modelo trabaja con Female o Male.",
    suggestions: ["Female", "Male"],
    parse(value) {
      const normalized = value.trim().toLowerCase();
      if (normalized === "female" || normalized === "mujer") {
        return { ok: true, value: "Female" };
      }
      if (normalized === "male" || normalized === "hombre") {
        return { ok: true, value: "Male" };
      }
      return { ok: false, error: "Responde con Female o Male para mantener la compatibilidad con el modelo actual." };
    },
  },
  {
    field: "degree",
    prompt: "¿Qué titulación o etapa académica estás cursando?",
    help: "Ejemplos: BSc, BA, B.Tech, MBA, MSc, PhD.",
    suggestions: ["BSc", "BA", "MBA"],
    parse(value) {
      const cleaned = value.trim();
      if (!cleaned) {
        return { ok: false, error: "Necesito una titulación o etapa académica para continuar." };
      }
      return { ok: true, value: cleaned };
    },
  },
  {
    field: "academic_pressure",
    prompt: "En una escala de 0 a 5, ¿cuánta presión académica sientes ahora mismo?",
    help: "0 significa nada de presión y 5 presión muy alta.",
    suggestions: ["1", "3", "5"],
    parse: parseScale(0, 5),
  },
  {
    field: "study_satisfaction",
    prompt: "En esa misma escala de 0 a 5, ¿cómo valorarías tu satisfacción con los estudios?",
    help: "0 es nada satisfecho y 5 muy satisfecho.",
    suggestions: ["1", "3", "5"],
    parse: parseScale(0, 5),
  },
  {
    field: "work_pressure",
    prompt: "Si compaginas trabajo con estudio, ¿qué presión laboral notas de 0 a 5?",
    help: "Si no aplica, puedes responder 0.",
    suggestions: ["0", "2", "4"],
    parse: parseScale(0, 5),
  },
  {
    field: "work_study_hours",
    prompt: "¿Cuántas horas al día dedicas normalmente a trabajo o estudio?",
    help: "El modelo acepta entre 0 y 12 horas.",
    suggestions: ["4", "7", "10"],
    parse: parseScale(0, 12),
  },
  {
    field: "sleep_duration",
    prompt: "¿Cómo describirías tu sueño últimamente?",
    help: "Puedes elegir una de las categorías del modelo.",
    suggestions: ["Less than 5 hours", "5-6 hours", "7-8 hours"],
    parse(value) {
      const normalized = value.trim().toLowerCase();
      const mapping = {
        "less than 5 hours": "Less than 5 hours",
        "menos de 5 horas": "Less than 5 hours",
        "5-6 hours": "5-6 hours",
        "5-6 horas": "5-6 hours",
        "7-8 hours": "7-8 hours",
        "7-8 horas": "7-8 hours",
        "more than 8 hours": "More than 8 hours",
        "mas de 8 horas": "More than 8 hours",
        "más de 8 horas": "More than 8 hours",
        others: "Others",
        otro: "Others",
      };
      const selected = mapping[normalized];
      if (!selected) {
        return { ok: false, error: "Prueba con: Less than 5 hours, 5-6 hours, 7-8 hours, More than 8 hours o Others." };
      }
      return { ok: true, value: selected };
    },
  },
  {
    field: "financial_stress",
    prompt: "En una escala de 1 a 5, ¿cómo describirías tu estrés financiero?",
    help: "1 es muy bajo y 5 muy alto.",
    suggestions: ["1", "3", "5"],
    parse: parseScale(1, 5),
  },
  {
    field: "dietary_habits",
    prompt: "¿Cómo describirías tus hábitos alimentarios en este momento?",
    help: "Puedes elegir Healthy, Moderate, Unhealthy u Others.",
    suggestions: ["Healthy", "Moderate", "Unhealthy"],
    parse(value) {
      const normalized = value.trim().toLowerCase();
      const mapping = {
        healthy: "Healthy",
        saludable: "Healthy",
        moderate: "Moderate",
        moderado: "Moderate",
        unhealthy: "Unhealthy",
        poco_saludable: "Unhealthy",
        "poco saludable": "Unhealthy",
        others: "Others",
        otro: "Others",
      };
      const selected = mapping[normalized];
      if (!selected) {
        return { ok: false, error: "Necesito una categoría clara: Healthy, Moderate, Unhealthy u Others." };
      }
      return { ok: true, value: selected };
    },
  },
  {
    field: "cgpa",
    prompt: "Si te encaja, ¿cuál es tu nota media aproximada en una escala de 0 a 10?",
    help: "Puedes responder con decimales.",
    suggestions: ["6.5", "7.5", "8.5"],
    parse: parseScale(0, 10),
  },
  {
    field: "job_satisfaction",
    prompt: "En una escala de 0 a 4, ¿qué satisfacción tienes con tu trabajo actual?",
    help: "Si no trabajas, puedes indicar 0.",
    suggestions: ["0", "2", "4"],
    parse: parseScale(0, 4),
  },
  {
    field: "suicidal_thoughts",
    prompt: "¿Has tenido pensamientos autolesivos o suicidas alguna vez?",
    help: "Responde Yes o No. Si esto te preocupa, busca ayuda profesional cuanto antes.",
    suggestions: ["No", "Yes"],
    parse: parseBooleanText(),
  },
  {
    field: "family_history",
    prompt: "¿Hay antecedentes familiares de enfermedad mental?",
    help: "Responde Yes o No.",
    suggestions: ["No", "Yes"],
    parse: parseBooleanText(),
  },
];

function parseScale(min, max) {
  return (value) => {
    const number = Number.parseFloat(value.replace(",", "."));
    if (Number.isNaN(number) || number < min || number > max) {
      return { ok: false, error: `Necesito un valor entre ${min} y ${max}.` };
    }
    return { ok: true, value: number };
  };
}

function parseBooleanText() {
  return (value) => {
    const normalized = value.trim().toLowerCase();
    if (["yes", "si", "sí"].includes(normalized)) {
      return { ok: true, value: "Yes" };
    }
    if (["no"].includes(normalized)) {
      return { ok: true, value: "No" };
    }
    return { ok: false, error: "Responde con Yes o No para mantener la consistencia del modelo." };
  };
}

function createMessage(role, text, options = {}) {
  return {
    id: `${role}-${crypto.randomUUID()}`,
    role,
    text,
    timestamp: Date.now(),
    ...options,
  };
}

const wait = (ms) => new Promise((resolve) => {
  window.setTimeout(resolve, ms);
});

export function useChatFlow() {
  const navigate = useNavigate();
  const {
    answers,
    messages,
    progress,
    patchAnswer,
    setMessages,
    setResult,
  } = useAssessmentState();
  const [isTyping, setIsTyping] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const currentQuestionIndex = QUESTIONS.findIndex((question) => {
    const value = answers[question.field];
    return value === null || value === "";
  });

  const currentQuestion = currentQuestionIndex === -1 ? null : QUESTIONS[currentQuestionIndex];

  useEffect(() => {
    if (messages.length > 0) {
      return;
    }

    setMessages((current) => {
      if (current.length > 0) {
        return current;
      }

      return [
        createMessage(
          "bot",
          "Gracias por estar aquí. Vamos paso a paso. Esta conversación es orientativa y busca recoger información para una predicción basada en datos.",
        ),
        createMessage(
          "bot",
          `${QUESTIONS[0].prompt} ${QUESTIONS[0].help}`,
        ),
      ];
    });
  }, [messages.length, setMessages]);

  const submitAnswer = async (rawValue) => {
    if (!currentQuestion || isTyping || isSubmitting) {
      return;
    }

    const value = rawValue.trim();
    if (!value) {
      return;
    }

    const userMessage = createMessage("user", value);
    setMessages((current) => [...current, userMessage]);

    const parsed = currentQuestion.parse(value);
    if (!parsed.ok) {
      setIsTyping(true);
      await wait(500);
      setMessages((current) => [
        ...current,
        createMessage("bot", parsed.error),
      ]);
      setIsTyping(false);
      return;
    }

    patchAnswer(currentQuestion.field, parsed.value);

    const nextQuestion = QUESTIONS[currentQuestionIndex + 1];
    setIsTyping(true);
    await wait(650);

    if (!nextQuestion) {
      setMessages((current) => [
        ...current,
        createMessage(
          "bot",
          "Gracias por compartirlo. Estoy organizando la información para darte una orientación clara y prudente.",
        ),
      ]);

      setIsSubmitting(true);
      const nextAnswers = {
        ...answers,
        [currentQuestion.field]: parsed.value,
      };

      try {
        const result = await predictAssessment(nextAnswers);
        setResult(result);
        await wait(700);
        navigate("/results");
      } catch (error) {
        setMessages((current) => [
          ...current,
          createMessage(
            "bot",
            "No he podido completar la evaluación ahora mismo. Puedes intentarlo de nuevo dentro de unos instantes.",
          ),
        ]);
      } finally {
        setIsTyping(false);
        setIsSubmitting(false);
      }

      return;
    }

    setMessages((current) => [
      ...current,
      createMessage(
        "bot",
        `Gracias por compartirlo. ${nextQuestion.prompt} ${nextQuestion.help}`,
      ),
    ]);
    setIsTyping(false);
  };

  return {
    messages,
    progress,
    currentQuestion,
    isTyping,
    isSubmitting,
    submitAnswer,
  };
}
