export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  safelist: [
    // Primary brand colour classes — always generate regardless of scanning
    'bg-brand-navy', 'bg-brand-blue', 'bg-brand-orange', 'bg-brand-yellow',
    'text-brand-navy', 'text-brand-blue', 'text-brand-orange', 'text-brand-yellow',
    'border-brand-navy', 'border-brand-blue', 'border-brand-orange',
    // Error/alert state colours
    'bg-bright-red-1', 'text-bright-red-3', 'border-bright-red-2',
  ],
  theme: {
    extend: {
      colors: {
        // ── Primary brand colours (Bright brand guidelines) ──────────────────
        'brand-navy':   '#0F2B3D',
        'brand-blue':   '#009FC7',
        'brand-orange': '#E39400',
        'brand-yellow': '#E6D600',

        // ── Extended tints/shades palette (Bright Figma design system) ───────
        // Level 3 is the primary colour; 1 = lightest, 5 = darkest
        'bright-navy': {
          1: '#8CA7B8',
          2: '#3B5C71',
          3: '#0F2B3D',
          4: '#081B27',
          5: '#000F1A',
        },
        'bright-blue': {
          1: '#9DDFEE',
          2: '#5BCAE3',
          3: '#00B0D8',
          4: '#007995',
          5: '#004858',
        },
        'bright-orange': {
          1: '#FFD39F',
          2: '#F4B56A',
          3: '#E39400',
          4: '#C65300',
          5: '#973600',
        },
        'bright-yellow': {
          1: '#FFEDAE',
          2: '#FFE176',
          3: '#E6D600',
          4: '#D1A300',
          5: '#9E6901',
        },
        'bright-purple': {
          1: '#CFBBF6',
          2: '#9F80DE',
          3: '#6F42C1',
          4: '#381774',
          5: '#1B004E',
        },
        'bright-pink': {
          1: '#FFA7CD',
          2: '#E85795',
          3: '#DB015F',
          4: '#9C0043',
          5: '#510023',
        },
        'bright-cyan': {
          1: '#A6E3D6',
          2: '#76D6C1',
          3: '#2FBF9F',
          4: '#008D6E',
          5: '#005542',
        },
        'bright-red': {
          1: '#FFADAD',
          2: '#FF7485',
          3: '#F2103D',
          4: '#B2000B',
          5: '#740007',
        },
        'bright-green': {
          1: '#A5F5CA',
          2: '#3EDF88',
          3: '#00893F',
          4: '#005C2A',
          5: '#00391C',
        },
      },
      fontFamily: {
        heading: ['"Museo Sans"', 'Nunito', 'system-ui', 'sans-serif'],
        sans: ['"Open Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
