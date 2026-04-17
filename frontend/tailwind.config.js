export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  safelist: [
    // Brand color classes — always generate regardless of scanning
    'bg-brand-navy', 'bg-brand-blue', 'bg-brand-orange', 'bg-brand-yellow',
    'text-brand-navy', 'text-brand-blue', 'text-brand-orange', 'text-brand-yellow',
    'border-brand-navy', 'border-brand-blue', 'border-brand-orange',
  ],
  theme: {
    extend: {
      colors: {
        'brand-navy':  '#0F2B3D',
        'brand-blue':  '#009FC7',
        'brand-orange':'#E39400',
        'brand-yellow':'#E6D600',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
