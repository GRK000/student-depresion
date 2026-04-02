import { createContext, useContext, useMemo, useState } from "react";

const defaultAnswers = {
  age: null,
  gender: "",
  degree: "",
  academic_pressure: null,
  study_satisfaction: null,
  work_pressure: null,
  work_study_hours: null,
  sleep_duration: "",
  financial_stress: null,
  dietary_habits: "",
  cgpa: null,
  job_satisfaction: null,
  suicidal_thoughts: "",
  family_history: "",
};

const AssessmentStateContext = createContext(null);

function calculateProgress(answers) {
  const total = Object.keys(defaultAnswers).length;
  const completed = Object.values(answers).filter((value) => value !== null && value !== "").length;
  return Math.round((completed / total) * 100);
}

export function AssessmentProvider({ children }) {
  const [answers, setAnswers] = useState(defaultAnswers);
  const [messages, setMessages] = useState([]);
  const [result, setResult] = useState(null);
  const [hasAcceptedDisclaimer, setHasAcceptedDisclaimer] = useState(false);
  const [sessionStartedAt, setSessionStartedAt] = useState(null);

  const progress = calculateProgress(answers);

  const patchAnswer = (field, value) => {
    setAnswers((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const restartAssessment = () => {
    setAnswers(defaultAnswers);
    setMessages([]);
    setResult(null);
    setSessionStartedAt(new Date().toISOString());
  };

  const startAssessment = () => {
    setHasAcceptedDisclaimer(true);
    setAnswers(defaultAnswers);
    setMessages([]);
    setResult(null);
    setSessionStartedAt(new Date().toISOString());
  };

  const exitAssessment = () => {
    setHasAcceptedDisclaimer(false);
    setAnswers(defaultAnswers);
    setMessages([]);
    setResult(null);
    setSessionStartedAt(null);
  };

  const value = useMemo(
    () => ({
      answers,
      messages,
      progress,
      result,
      hasAcceptedDisclaimer,
      sessionStartedAt,
      patchAnswer,
      setMessages,
      setResult,
      startAssessment,
      restartAssessment,
      exitAssessment,
    }),
    [answers, messages, progress, result, hasAcceptedDisclaimer, sessionStartedAt],
  );

  return (
    <AssessmentStateContext.Provider value={value}>
      {children}
    </AssessmentStateContext.Provider>
  );
}

export function useAssessmentState() {
  const context = useContext(AssessmentStateContext);

  if (!context) {
    throw new Error("useAssessmentState must be used within AssessmentProvider");
  }

  return context;
}
