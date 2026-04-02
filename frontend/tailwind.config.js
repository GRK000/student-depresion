/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F7FAFC",
        surface: "#FFFFFF",
        primary: "#4A90E2",
        "primary-dark": "#357ABD",
        secondary: "#6FCF97",
        ink: "#1F2937",
        muted: "#6B7280",
        border: "#E5E7EB",
        danger: "#E67E80",
        warning: "#F2C94C",
        success: "#6FCF97",
        "user-bubble": "#EAF3FF",
      },
      boxShadow: {
        soft: "0 12px 30px rgba(31, 41, 55, 0.06)",
        card: "0 18px 45px rgba(53, 122, 189, 0.08)",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Manrope", "Inter", "sans-serif"],
      },
      backgroundImage: {
        "page-glow":
          "radial-gradient(circle at top left, rgba(74, 144, 226, 0.12), transparent 35%), radial-gradient(circle at bottom right, rgba(111, 207, 151, 0.14), transparent 32%)",
      },
    },
  },
  plugins: [],
};
