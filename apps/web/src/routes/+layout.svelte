<script lang="ts">
  import { onMount } from 'svelte';
  import { setupI18n } from '$lib/i18n';

  onMount(() => {
    void setupI18n();
  });
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.gstatic.com" />
  <link
    rel="stylesheet"
    href="https://fonts.cdnfonts.com/css/dejavu-sans"
  />
</svelte:head>

<main>
  <slot />
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'DejaVu Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI',
      sans-serif;
    background: #f5f5f7;
    color: #1f1f1f;
  }

  main {
    min-height: 100vh;
  }
</style>
