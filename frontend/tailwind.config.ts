import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202A",
        cloud: "#F6F8FA",
        line: "#DDE3EA",
        teal: "#0F766E",
        amber: "#B45309",
        rose: "#BE123C",
      },
    },
  },
  plugins: [],
};

export default config;
