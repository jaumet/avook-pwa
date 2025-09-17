<script lang="ts">
  export let data: { token?: string } = {};
</script>

<section class="access">
  <h1>Access Audiovook</h1>
  <p data-testid="access-placeholder">
    This page will guide listeners through validating their QR code token.
  </p>
  {#if data.token}
    <p class="token">Token: {data.token}</p>
  {:else}
    <p class="token token--missing">Provide a token query parameter to continue.</p>
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

  .token--missing {
    color: #a33;
  }
</style>
