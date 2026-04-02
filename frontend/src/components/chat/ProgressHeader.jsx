import { LogOut, RotateCcw } from "lucide-react";

import Button from "../ui/Button";
import BrandMark from "../ui/BrandMark";

function ProgressHeader({ progress, onExit, onRestart }) {
  return (
    <header className="sticky top-0 z-20 rounded-[28px] border border-white/70 bg-white/85 px-4 py-4 shadow-soft backdrop-blur md:px-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <BrandMark compact />

        <div className="flex-1 lg:max-w-md">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium text-ink">Información recopilada</span>
            <span className="text-muted">{progress}%</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-primary transition-all duration-700 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-2 self-end lg:self-auto">
          <Button variant="ghost" size="sm" onClick={onRestart}>
            <RotateCcw size={16} />
            Reiniciar
          </Button>
          <Button variant="secondary" size="sm" onClick={onExit}>
            <LogOut size={16} />
            Salir
          </Button>
        </div>
      </div>
    </header>
  );
}

export default ProgressHeader;
