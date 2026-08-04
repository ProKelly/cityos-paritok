/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{vue,js,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        // "Night chart" palette — a navigator's chart at dusk.
        // Full numeric scales (50-950) so standard Tailwind conventions like
        // `text-chart-400` or `border-navy-500` resolve everywhere, not just
        // the original DEFAULT/dim shorthand.
        navy: {
          50: "#F4F5FA",
          100: "#DEE1F0",
          200: "#B9C0DE",
          300: "#8D97C4",
          400: "#6673A8",
          500: "#4A5488",
          600: "#333C68",
          700: "#262E52",
          800: "#1B2140",
          900: "#12172B",
          950: "#0B0F1F",
        },
        parchment: {
          DEFAULT: "#F6F4EC",
          50: "#FFFFFF",
          100: "#FEFDFB",
          200: "#FAF9F3",
          300: "#F6F4EC",
          400: "#F6F4EC",
          500: "#E4E0D0",
          600: "#C7C1A8",
        },
        signal: {
          DEFAULT: "#F2B84B", // beacon gold — primary accent
          dim: "#C9922E",
          50: "#FDF6E9",
          100: "#FBEBCB",
          200: "#F8DAA1",
          300: "#F5C976",
          400: "#F2B84B",
          500: "#DBA234",
          600: "#C9922E",
          700: "#9C7124",
        },
        chart: {
          DEFAULT: "#4FD1C5", // charted-route teal — secondary accent
          dim: "#2E9A90",
          50: "#EFFDFB",
          100: "#D3F7F2",
          200: "#A9ECE4",
          300: "#7FE0D6",
          400: "#4FD1C5",
          500: "#3FBBAF",
          600: "#2E9A90",
          700: "#237570",
        },
        coral: {
          DEFAULT: "#EF7B6A",
          50: "#FDF0EE",
          100: "#FADAD4",
          200: "#F5B5AA",
          300: "#F29B8B",
          400: "#EF7B6A",
          500: "#E4573F",
          600: "#C13F29",
        },
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "star-field":
          "radial-gradient(circle at 20% 20%, rgba(242,184,75,0.08), transparent 35%), radial-gradient(circle at 80% 0%, rgba(79,209,197,0.10), transparent 40%), radial-gradient(circle at 50% 100%, rgba(79,209,197,0.06), transparent 45%)",
      },
      boxShadow: {
        beacon: "0 0 0 1px rgba(242,184,75,0.25), 0 8px 30px -8px rgba(242,184,75,0.35)",
        chart: "0 8px 30px -12px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};