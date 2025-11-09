/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Pure black background
        'cyber-black': '#000000',
        // Gradient backgrounds
        'cyber-purple': '#1a0033',
        'cyber-blue': '#000d1a',
        // Primary neon cyan
        'neon-cyan': '#00ffff',
        'neon-cyan-dark': '#00cccc',
        // Secondary electric purple
        'electric-purple': '#a855f7',
        'electric-purple-dark': '#8b44d6',
        // Success/XP neon green
        'neon-green': '#00ff00',
        'neon-green-dark': '#00cc00',
        // Warning neon orange
        'neon-orange': '#ff6b00',
        'neon-orange-dark': '#cc5500',
        // Error red
        'neon-red': '#ff0055',
        // Text colors
        'text-primary': '#e0e0e0',
        'text-secondary': '#a0a0a0',
        'text-muted': '#606060',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(135deg, #1a0033 0%, #000d1a 100%)',
        'cyber-gradient-radial': 'radial-gradient(circle at top right, #1a0033, #000000)',
      },
      boxShadow: {
        'neon-cyan': '0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff',
        'neon-purple': '0 0 10px #a855f7, 0 0 20px #a855f7, 0 0 30px #a855f7',
        'neon-green': '0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'glow': 'glow 3s ease-in-out infinite',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        'glow': {
          '0%, 100%': { boxShadow: '0 0 5px currentColor' },
          '50%': { boxShadow: '0 0 20px currentColor' },
        },
      },
    },
  },
  plugins: [],
}
