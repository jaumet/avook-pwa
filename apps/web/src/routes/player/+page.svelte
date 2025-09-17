<script lang="ts">
  import { t } from 'svelte-i18n';
  let isPlaying = false;

  const togglePlayback = () => {
    isPlaying = !isPlaying;
  };
</script>

<section class="player">
  <h1>{$t('player.title')}</h1>
  <p>{$t('player.description')}</p>
  <button class="player__button" type="button" on:click={togglePlayback}>
    {isPlaying ? $t('player.pause') : $t('player.play')}
  </button>
</section>

<style>
  .player {
    padding: 2rem;
    text-align: center;
  }

  .player__button {
    margin-top: 1.5rem;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
    border-radius: 9999px;
    border: none;
    background: #1a73e8;
    color: #fff;
    cursor: pointer;
  }

  .player__button:focus {
    outline: 3px solid rgba(26, 115, 232, 0.4);
    outline-offset: 3px;
  }
</style>
