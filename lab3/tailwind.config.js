/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#6366f1',
                'primary-hover': '#4f46e5',
                'dark-bg': '#0f172a',
                'card-bg': 'rgba(30, 41, 59, 0.7)',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
