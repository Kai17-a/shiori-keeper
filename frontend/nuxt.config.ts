export default defineNuxtConfig({
    compatibilityDate: "2025-04-07",
    devtools: { enabled: false },
    ssr: false,
    app: {
        head: {
            title: "Bookmark Manager",
            meta: [
                {
                    name: "viewport",
                    content: "width=device-width, initial-scale=1",
                },
            ],
        },
    },
    runtimeConfig: {
        public: {
            apiBase:
                process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8001",
        },
    },
});
