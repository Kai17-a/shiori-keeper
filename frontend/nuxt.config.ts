const env =
    (globalThis as {
        process?: { env?: Record<string, string | undefined> };
    }).process?.env ?? {};

export default defineNuxtConfig({
    modules: ["@nuxt/ui"],

    devtools: { enabled: false },
    css: ["~/assets/css/main.css"],
    ssr: false,
    vite: {
        build: {
            modulePreload: {
                polyfill: false,
            },
        },
    },
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

    compatibilityDate: "2025-04-07",

    runtimeConfig: {
        public: {
            apiBaseUrl:
                env.NUXT_PUBLIC_API_BASE_URL ||
                env.NUXT_PUBLIC_API_BASE ||
                "http://localhost:8000",
        },
    },
});
