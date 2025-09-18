<script lang="ts">
  import type { PageData } from './$types';
  import { t } from 'svelte-i18n';

  export let data: PageData;
</script>

<section class="access">
  <h1>{$t('access.title')}</h1>
  <p data-testid="access-placeholder">{$t('access.placeholder')}</p>
  {#if data.token}
    <p class="token">
      {$t('access.token')}: <span>{data.token}</span>
    </p>
  {:else}
    <p class="token token--missing">{$t('access.token_missing')}</p>
  {/if}
</section>

<style>
  .access {
    padding: 2rem;
    max-width: 48rem;
    margin: 0 auto;
  }

  .token {
    margin-top: 1rem;
    font-family: monospace;
  }

  .token span {
    word-break: break-all;
  }

  .token--missing {
    color: #a33;
  }
</style>
