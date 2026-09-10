// Tailwind configuration.
//
// Colors and fonts here implement the CareBridge-AI design system:
// a deep clinical blue paired with a teal-green accent, set in
// Fraunces (headings) and Inter (body/forms) to feel trustworthy
// and calm rather than like a generic SaaS dashboard.
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1877F2',
          light: '#3D8CF5',
          dark: '#0E56B5',
        },
        accent: {
          DEFAULT: '#35A477',
          light: '#55BA91',
          dark: '#237451',
        },
        surface: {
          DEFAULT: '#EEF5FF',
          dark: '#111D2D',
        },
        panel: {
          DEFAULT: '#FFFFFF',
          dark: '#19283B',
        },
        ink: {
          DEFAULT: '#142B4A',
          dark: '#EAF2FC',
        },
        muted: {
          DEFAULT: '#66768C',
          dark: '#9EADBF',
        },
        danger: '#C0533E',
      },
      fontFamily: {
        display: ['Fraunces', 'serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
