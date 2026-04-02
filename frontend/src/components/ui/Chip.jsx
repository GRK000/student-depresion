function Chip({ children, className = "", active = false, ...props }) {
  return (
    <button
      type="button"
      className={`inline-flex items-center rounded-full border px-3.5 py-2 text-sm transition duration-200 ${
        active
          ? "border-primary bg-primary/10 text-primary-dark"
          : "border-border bg-white text-muted hover:border-primary/35 hover:bg-primary/5 hover:text-ink"
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export default Chip;
