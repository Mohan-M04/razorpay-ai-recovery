/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fintech: {
          dark: '#080C14',
          card: '#0F172A',
          border: '#1E293B',
          accent: '#2563EB',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#EF4444',
          muted: '#64748B'
        }
      }
    },
  },
  plugins: [],
}
