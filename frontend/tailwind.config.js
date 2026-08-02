/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#150f1e",
        surface: "#201731",
        surface2: "#2a1f40",
        line: "#3a2c54",
        gold: "#d7a83f",
        gold2: "#f0c667",
        mulberry: "#c1447e",
        mulberry2: "#e069a0",
        text: "#f2ecf9",
        muted: "#a99cc2",
        danger: "#e0587a",
      },
    },
  }, 
  plugins: [],
};
