<script lang="ts">
  import { t } from 'svelte-i18n';
</script>

<section class="error">
  <h1>{$t('error.title')}</h1>
  <p>{$t('error.description')}</p>
</section>

<style>
  .error {
    padding: 4rem 2rem;
    text-align: center;
  }

  .error h1 {
    color: #b00020;
  }
</style>
