import { Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Assessment from "./pages/Assessment";
import Results from "./pages/Results";
import About from "./pages/About";

function App() {
  return (
    <div className="min-h-screen bg-canvas bg-page-glow text-ink">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-[-8rem] top-[-8rem] h-64 w-64 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-[-10rem] right-[-6rem] h-72 w-72 rounded-full bg-secondary/15 blur-3xl" />
      </div>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/assessment" element={<Assessment />} />
        <Route path="/results" element={<Results />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </div>
  );
}

export default App;
