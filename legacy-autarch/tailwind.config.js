/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        cookie: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          300: '#e0a96d',
          400: '#c38d50',
          500: '#a67038',
          600: '#7c4d25',
          700: '#5e381b',
          800: '#3d2311',
          900: '#201209',
        },
        cyber: {
          bg: '#0a0b0e',
          card: '#12141c',
          border: '#232738',
          accent: '#e0a96d',
          neon: '#00f2fe',
          purple: '#9d4edd',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
};
