/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        qx: {
          bg: "#07090e",
          card: "#0c1018",
          panel: "#101520",
          green: "#00d4a0",
          blue: "#4d9fff",
          yellow: "#ffc857",
          red: "#ff4d6d",
          purple: "#a78bfa",
          t1: "#dde4f0",
          t2: "#7a8699",
          t3: "#3d4a5e",
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
