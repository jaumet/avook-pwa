<script lang="ts">
  import { t } from 'svelte-i18n';

  import type { AccessPageData } from './resolve';

  export let data: AccessPageData;

  const statusTranslationMap: Record<string, string> = {
    new: 'access.status.new',
    registered: 'access.status.registered',
    blocked: 'access.status.blocked'
  };
</script>

<section class="access">
  <h1>{$t('access.title')}</h1>
  <p class="intro">{$t('access.placeholder')}</p>

  {#if data.token}
    <p class="token">
      <span class="token__label">{$t('access.token_label')}:</span>
      <span class="token__value">{data.token}</span>
    </p>
  {/if}

  {#if data.tokenStatus === 'missing'}
    <p class="notice notice--info">{$t('access.token_missing')}</p>
    <div class="demo">
      <h2>{$t('access.demo_tokens_title')}</h2>
      <p>{$t('access.demo_tokens_description')}</p>
      <ul>
        {#each data.demoTokens as token}
          <li>
            <a class="demo__link" href={`/access/${token}`}>
              <code>{token}</code>
            </a>
          </li>
        {/each}
      </ul>
    </div>
  {:else if data.tokenStatus === 'invalid'}
    <p class="notice notice--error">{$t('access.token_invalid')}</p>
  {:else if data.tokenStatus === 'error'}
    <p class="notice notice--error">{$t('access.token_error')}</p>
    {#if data.error}
      <pre class="error-detail">{data.error}</pre>
    {/if}
  {:else}
    {#if statusTranslationMap[data.tokenStatus]}
      <p class={`notice notice--status notice--${data.tokenStatus}`}>
        {$t(statusTranslationMap[data.tokenStatus])}
      </p>
    {/if}

    {#if data.validation?.product}
      <p class="product">
        {$t('access.product', { values: { id: data.validation.product.id } })}
        {#if data.validation.product.title}
          <span class="product__title">— {data.validation.product.title}</span>
        {/if}
      </p>
    {/if}

    <dl class="details">
      <div>
        <dt>{$t('access.preview')}</dt>
        <dd>
          {data.validation?.preview_available
            ? $t('access.available')
            : $t('access.unavailable')}
        </dd>
      </div>
      <div>
        <dt>{$t('access.can_reregister')}</dt>
        <dd>{data.validation?.can_reregister ? $t('access.yes') : $t('access.no')}</dd>
      </div>
      {#if data.validation?.cooldown_until}
        <div>
          <dt>{$t('access.cooldown')}</dt>
          <dd>{new Date(data.validation.cooldown_until).toLocaleString()}</dd>
        </div>
      {/if}
    </dl>
  {/if}
</section>

<style>
  .access {
    padding: 2rem;
    max-width: 48rem;
    margin: 0 auto;
  }

  .intro {
    margin-bottom: 1.5rem;
  }

  .token {
    display: flex;
    gap: 0.5rem;
    font-family: var(--font-mono, monospace);
    margin-bottom: 1.5rem;
    align-items: baseline;
  }

  .token__label {
    font-weight: 600;
  }

  .token__value {
    word-break: break-all;
  }

  .notice {
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    margin-bottom: 1.5rem;
    background: #f1f5f9;
    color: #0f172a;
  }

  .notice--info {
    border: 1px solid #38bdf8;
  }

  .notice--error {
    border: 1px solid #f87171;
    background: #fef2f2;
    color: #7f1d1d;
  }

  .notice--status {
    border: 1px solid #22c55e;
    background: #f0fdf4;
    color: #14532d;
  }

  .notice--registered {
    border-color: #818cf8;
    background: #eef2ff;
    color: #312e81;
  }

  .notice--blocked {
    border-color: #f97316;
    background: #fff7ed;
    color: #7c2d12;
  }

  .demo ul {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    padding: 0;
    margin: 0.5rem 0 0;
    list-style: none;
  }

  .demo__link {
    text-decoration: none;
  }

  .demo code {
    background: #0f172a;
    color: #f8fafc;
    padding: 0.4rem 0.65rem;
    border-radius: 0.5rem;
    font-size: 0.95rem;
    display: inline-block;
    transition: background 0.2s ease, transform 0.2s ease;
  }

  .demo__link:focus code,
  .demo__link:hover code {
    background: #1e293b;
    transform: translateY(-1px);
  }

  .product {
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .product__title {
    font-style: italic;
    font-weight: 400;
  }

  .details {
    display: grid;
    gap: 0.75rem;
  }

  .details dt {
    font-weight: 600;
  }

  .details dd {
    margin: 0;
  }

  .error-detail {
    margin: 0;
    padding: 1rem;
    border-radius: 0.5rem;
    background: #0f172a;
    color: #f8fafc;
    font-family: var(--font-mono, monospace);
    overflow-x: auto;
  }
</style>

