import { defineConfig } from "wxt";
import vue from "@vitejs/plugin-vue";
import ui from "@nuxt/ui/vite";

// See https://wxt.dev/api/config.html
export default defineConfig({
  manifest: {
    name: "Shiori Keeper",
    version: "0.1.0",
    description: "An extension for Shiori Keeper.",
    icons: ["32.png", "64.png", "128.png"],
    action: {
      default_popup: "popup.html",
      default_title: "Shiori Keeper",
    },
    permissions: ["tabs", "storage", "bookmarks"],
    host_permissions: ["<all_urls>"],
    content_security_policy: {
      extension_pages: "script-src 'self'; style-src 'self' 'unsafe-inline';",
    },
  },

  modules: ["@wxt-dev/module-vue"],
  vite: () => ({
    plugins: [
      ui({
        ui: {
          colors: {
            neutral: "neutral",
          },
        },
      }),
    ],
  }),
});
