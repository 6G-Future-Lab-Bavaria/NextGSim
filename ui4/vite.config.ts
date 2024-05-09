import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { resolve } from "path"

// https://vitejs.dev/config/

console.log(resolve(__dirname, './src/pages/index/main.ts'));


export default defineConfig(({mode}) => { return {
  plugins: [svelte({
    prebundleSvelteLibraries: false
  })],
  build: {
    target: "es2015",
    lib: {
      entry: {
        index: resolve(__dirname, './src/pages/index/main.ts'),
        project: resolve(__dirname, './src/pages/project/main.ts'),
        run: resolve(__dirname, './src/pages/run/main.ts'),
      },
      formats: [ "es" ],
    },
    // @ts-ignore
    sourcemap: mode == "development" ? "inline" : false,
    // cssCodeSplit: true,
  },
  optimizeDeps: {
    force: true,
  }
};})
