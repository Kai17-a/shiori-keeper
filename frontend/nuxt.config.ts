import tailwindcss from "@tailwindcss/vite";

export default defineNuxtConfig({
  modules: ["@nuxt/ui"],

  devtools: { enabled: false },
  css: ["~/assets/css/main.css"],
  ssr: false,
  sourcemap: {
    client: true,
    server: false,
  },
  vite: {
    logLevel: "error",
    server: {
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
    build: {
      sourcemap: true,
      modulePreload: {
        polyfill: false,
      },
    },
    css: {
      devSourcemap: true,
    },
  },
  app: {
    head: {
      title: "Shiori Keeper",
      meta: [
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1",
        },
      ],
    },
  },
  compatibilityDate: "2025-04-07",
});
