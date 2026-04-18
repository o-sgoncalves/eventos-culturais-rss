/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          purple: '#6c63ff',
          teal: '#3ecfb2',
          dark: '#0f0f1a',
          card: '#16213e',
          border: '#2d2d4e',
          muted: '#9ca3af',
        },
      },
    },
  },
  plugins: [],
}
