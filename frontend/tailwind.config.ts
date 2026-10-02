import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        panel: '#0b1220',
        panelAlt: '#101a2a',
        accent: '#7c9cff',
        accentSoft: '#dfe7ff',
        success: '#34d399',
        warning: '#fbbf24',
        danger: '#f87171',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(124,156,255,0.35), 0 20px 40px rgba(15,23,42,0.35)',
      },
    },
  },
  plugins: [],
};

export default config;
