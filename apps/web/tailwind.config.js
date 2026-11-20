/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        polaris: {
          app: 'var(--bg-app)',
          surface: 'var(--bg-surface)',
          secondary: 'var(--bg-surface-secondary)',
          hover: 'var(--bg-surface-hover)',
          border: 'var(--border-subtle)',
          'border-base': 'var(--border-base)',
          text: 'var(--text-primary)',
          'text-secondary': 'var(--text-secondary)',
          'text-subdued': 'var(--text-subdued)',
          accent: 'var(--color-accent)',
          'accent-hover': 'var(--color-accent-hover)',
          'accent-subtle': 'var(--color-accent-subtle)',
        },
      },
      borderRadius: {
        'polaris-xs': 'var(--radius-xs)',
        'polaris-sm': 'var(--radius-sm)',
        'polaris-md': 'var(--radius-md)',
        'polaris-lg': 'var(--radius-lg)',
        'polaris-xl': 'var(--radius-xl)',
      },
    },
  },
  plugins: [],
}
