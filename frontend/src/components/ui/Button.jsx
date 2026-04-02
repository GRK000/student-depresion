function getVariantClasses(variant) {
  if (variant === "secondary") {
    return "bg-white text-ink border border-border hover:border-primary/40 hover:bg-slate-50";
  }
  if (variant === "ghost") {
    return "bg-transparent text-muted hover:bg-white/80 hover:text-ink";
  }
  return "bg-primary text-white hover:bg-primary-dark";
}

function getSizeClasses(size) {
  if (size === "sm") {
    return "h-10 px-4 text-sm";
  }
  if (size === "lg") {
    return "h-14 px-6 text-base";
  }
  return "h-12 px-5 text-sm";
}

function Button({
  as: Component = "button",
  to,
  children,
  className = "",
  variant = "primary",
  size = "md",
  type = "button",
  ...props
}) {
  const sharedClassName = `inline-flex items-center justify-center gap-2 rounded-full font-medium transition duration-200 disabled:cursor-not-allowed disabled:opacity-55 ${getVariantClasses(variant)} ${getSizeClasses(size)} ${className}`;

  if (Component !== "button") {
    return (
      <Component
        to={to}
        className={sharedClassName}
        {...props}
      >
        {children}
      </Component>
    );
  }

  return (
    <Component
      type={type}
      className={sharedClassName}
      {...props}
    >
      {children}
    </Component>
  );
}

export default Button;
