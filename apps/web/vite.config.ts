import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 5173
  },
  resolve: {
    alias: {
      deepmerge: 'deepmerge/dist/esm.js'
    }
  },
  optimizeDeps: {
    exclude: ['svelte-i18n', 'intl-messageformat', 'deepmerge']
  }
});
