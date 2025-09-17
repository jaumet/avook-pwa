<script lang="ts">
  let isPlaying = false;

  const togglePlayback = () => {
    isPlaying = !isPlaying;
  };
</script>

<section class="player">
  <h1>Player Placeholder</h1>
  <p>The full-featured Audiovook player UI will live here.</p>
  <button class="player__button" type="button" on:click={togglePlayback}>
    {isPlaying ? 'Pause' : 'Play'}
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
