import { HeartPulse } from "lucide-react";
import { Link } from "react-router-dom";

function BrandMark({ compact = false }) {
  return (
    <Link to="/" className="inline-flex items-center gap-3">
      <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/12 text-primary">
        <HeartPulse size={22} />
      </span>
      <span>
        <span className="block font-display text-base font-semibold text-ink">
          Wellbeing Compass
        </span>
        {!compact ? (
          <span className="block text-sm text-muted">Orientación conversacional y explicable</span>
        ) : null}
      </span>
    </Link>
  );
}

export default BrandMark;
