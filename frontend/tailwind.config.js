/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'nba-primary': '#1d428a',
        'nba-secondary': '#c8102e',
      },
    },
  },
  plugins: [],
}
