import vue from "@vitejs/plugin-vue2";
import { defineConfig } from "vite";
// import { createVuePlugin as vue } from "vite-plugin-vue2";
const path = require("path");

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname),
      "~": path.resolve(__dirname, "/node_modules/"),
      "@app": path.resolve(__dirname, "./app"),
    },
    extensions: [".mjs", ".js", ".ts", ".jsx", ".tsx", ".json", ".vue"],
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:9030",
        changeOrigin: true,
      },
    },
  },
});
