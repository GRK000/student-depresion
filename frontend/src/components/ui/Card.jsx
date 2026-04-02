function Card({ children, className = "" }) {
  return (
    <div className={`rounded-[28px] border border-border bg-surface shadow-card ${className}`}>
      {children}
    </div>
  );
}

export default Card;
