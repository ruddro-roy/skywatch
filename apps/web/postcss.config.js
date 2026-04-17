/** @type {import('postcss').Config} */
const config = {
  plugins: {
    // Tailwind CSS v4 uses @tailwindcss/postcss
    "@tailwindcss/postcss": {},
    autoprefixer: {},
  },
};

module.exports = config;
