const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8083";

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function scorePayload(payload) {
  let score = 0.18;

  score += (payload.academic_pressure / 5) * 0.18;
  score += ((5 - payload.study_satisfaction) / 5) * 0.12;
  score += (payload.work_pressure / 5) * 0.07;
  score += (payload.work_study_hours / 12) * 0.08;
  score += ((payload.financial_stress - 1) / 4) * 0.12;
  score += payload.sleep_duration === "Less than 5 hours" ? 0.12 : 0;
  score += payload.sleep_duration === "5-6 hours" ? 0.05 : 0;
  score += payload.dietary_habits === "Unhealthy" ? 0.06 : 0;
  score += payload.suicidal_thoughts === "Yes" ? 0.16 : 0;
  score += payload.family_history === "Yes" ? 0.05 : 0;
  score += payload.job_satisfaction <= 1 ? 0.03 : 0;
  score -= payload.sleep_duration === "7-8 hours" ? 0.05 : 0;
  score -= payload.dietary_habits === "Healthy" ? 0.03 : 0;
  score -= payload.study_satisfaction >= 4 ? 0.04 : 0;

  return clamp(score, 0.05, 0.96);
}

function buildFactors(payload) {
  const candidates = [
    payload.academic_pressure >= 4 && {
      title: "Estrés académico elevado",
      description: "La presión académica aparece en un nivel alto y puede amplificar la sensación de saturación.",
      tone: "high",
    },
    payload.sleep_duration === "Less than 5 hours" && {
      title: "Sueño insuficiente",
      description: "Dormir menos de cinco horas suele relacionarse con peor recuperación emocional y mental.",
      tone: "high",
    },
    payload.financial_stress >= 4 && {
      title: "Estrés financiero alto",
      description: "La presión económica sostenida puede aumentar la carga emocional del día a día.",
      tone: "medium",
    },
    payload.study_satisfaction <= 2 && {
      title: "Baja satisfacción académica",
      description: "Una satisfacción baja con los estudios puede ser una fuente adicional de malestar.",
      tone: "medium",
    },
    payload.work_study_hours >= 9 && {
      title: "Carga diaria intensa",
      description: "Muchas horas de estudio o trabajo pueden dejar poco margen para descanso y regulación.",
      tone: "medium",
    },
    payload.suicidal_thoughts === "Yes" && {
      title: "Señales de alarma reportadas",
      description: "Has indicado pensamientos autolesivos o suicidas alguna vez. Eso merece una atención responsable y cercana.",
      tone: "high",
    },
    payload.family_history === "Yes" && {
      title: "Antecedentes familiares relevantes",
      description: "Los antecedentes no determinan el resultado, pero sí aportan contexto al modelo.",
      tone: "low",
    },
    payload.dietary_habits === "Unhealthy" && {
      title: "Rutina física menos favorable",
      description: "Los hábitos alimentarios menos estables pueden acompañar periodos de desajuste general.",
      tone: "low",
    },
  ].filter(Boolean);

  if (candidates.length === 0) {
    return [
      {
        title: "Señales relativamente estables",
        description: "No se observan factores marcadamente intensos entre las variables más influyentes recogidas.",
        tone: "low",
      },
    ];
  }

  return candidates.slice(0, 4);
}

function getRiskLevel(probability) {
  if (probability >= 0.7) {
    return { label: "Alto", color: "danger" };
  }
  if (probability >= 0.42) {
    return { label: "Moderado", color: "warning" };
  }
  return { label: "Bajo", color: "success" };
}

function joinFactorTitles(factors) {
  const names = factors.map((factor) => factor.title.toLowerCase());
  if (names.length === 1) {
    return names[0];
  }
  if (names.length === 2) {
    return `${names[0]} y ${names[1]}`;
  }
  return `${names.slice(0, -1).join(", ")} y ${names.at(-1)}`;
}

function buildRecommendations(riskLevel) {
  const base = [
    "Esto no sustituye una valoración profesional. Tómalo como una orientación inicial.",
    "Si el malestar se mantiene, considera hablar con un profesional de salud mental o con el servicio de orientación de tu centro.",
  ];

  if (riskLevel.label === "Alto") {
    return [
      ...base,
      "Si sientes que tu seguridad podría estar en riesgo, busca apoyo inmediato en tu entorno cercano o en servicios profesionales de urgencia.",
    ];
  }

  if (riskLevel.label === "Moderado") {
    return [
      ...base,
      "Puede ser útil revisar descanso, carga académica y apoyos disponibles antes de que el malestar aumente.",
    ];
  }

  return [
    ...base,
    "Mantener rutinas de sueño, descansos y seguimiento personal puede ayudarte a sostener este equilibrio.",
  ];
}

function normalizeResult(payload, response) {
  const probability = response?.probability ?? scorePayload(payload);
  const prediction = response?.prediction ?? (probability >= 0.5 ? 1 : 0);
  const riskLevel = getRiskLevel(probability);
  const factors = buildFactors(payload);

  return {
    prediction,
    probability,
    riskLevel,
    factors,
    explanation:
      factors.length > 0
        ? `El resultado está influido sobre todo por ${joinFactorTitles(factors.slice(0, 3))}.`
        : "El resultado combina distintas señales del descanso, la presión académica y la rutina diaria.",
    summary:
      riskLevel.label === "Alto"
        ? "La combinación actual de señales merece atención cercana y un siguiente paso responsable."
        : riskLevel.label === "Moderado"
          ? "Hay indicios que conviene mirar con calma antes de que el malestar escale."
          : "La señal estimada es baja, aunque sigue siendo útil escuchar cómo te estás sintiendo.",
    recommendations: buildRecommendations(riskLevel),
    modelVersion: response?.model_version ?? "simulated-preview",
    payload,
  };
}

export async function predictAssessment(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Prediction failed with status ${response.status}`);
    }

    const data = await response.json();
    return normalizeResult(payload, data);
  } catch (error) {
    return normalizeResult(payload, null);
  }
}

export async function checkApiHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Health check failed");
  }
  return response.json();
}
