<script lang="ts">
  import { onMount } from 'svelte';
  import { t } from 'svelte-i18n';
  import { audioSamples } from '$lib/audio/samples';

  type Track = {
    id: string;
    titleKey: string;
    duration: number;
    source: string;
  };

  const tracks: Track[] = [
    {
      id: 'demo-intro',
      titleKey: 'player.tracks.intro',
      duration: 1,
      source: audioSamples.demoIntroSample
    },
    {
      id: 'demo-chapter',
      titleKey: 'player.tracks.chapter',
      duration: 1,
      source: audioSamples.demoChapterSample
    },
    {
      id: 'demo-outro',
      titleKey: 'player.tracks.outro',
      duration: 1,
      source: audioSamples.demoOutroSample
    }
  ];

  let audioElement: HTMLAudioElement;
  let currentTrackIndex = 0;
  let isPlaying = false;
  let progress = 0;
  let isSeeking = false;
  let displayedTime = 0;
  let totalDuration = tracks[0].duration;

  $: currentTrack = tracks[currentTrackIndex];

  const clamp = (value: number, min: number, max: number) =>
    Math.min(Math.max(value, min), max);

  const formatTime = (seconds: number) => {
    const totalSeconds = Math.max(0, Math.round(seconds));
    const minutes = Math.floor(totalSeconds / 60);
    const remaining = totalSeconds % 60;
    return `${minutes}:${remaining.toString().padStart(2, '0')}`;
  };

  const updateProgressFromAudio = () => {
    if (!audioElement || !audioElement.duration) {
      progress = 0;
      displayedTime = 0;
      totalDuration = currentTrack.duration;
      return;
    }

    totalDuration = audioElement.duration;
    displayedTime = audioElement.currentTime;
    progress = clamp((audioElement.currentTime / audioElement.duration) * 100, 0, 100);
  };

  const loadTrack = async (startPlaying: boolean) => {
    if (!audioElement) return;

    audioElement.src = currentTrack.source;
    audioElement.load();
    progress = 0;
    displayedTime = 0;
    totalDuration = currentTrack.duration;

    if (startPlaying) {
      try {
        await audioElement.play();
        isPlaying = true;
      } catch (error) {
        console.error('Unable to start playback', error);
        isPlaying = false;
      }
    }
  };

  const togglePlayback = async () => {
    if (!audioElement) return;

    if (isPlaying) {
      audioElement.pause();
      return;
    }

    try {
      await audioElement.play();
      isPlaying = true;
    } catch (error) {
      console.error('Playback error', error);
    }
  };

  const playTrackAt = (index: number) => {
    currentTrackIndex = index;
    void loadTrack(true);
  };

  const playNext = () => {
    if (currentTrackIndex < tracks.length - 1) {
      currentTrackIndex += 1;
      void loadTrack(true);
    } else {
      if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
      }
      isPlaying = false;
    }
  };

  const playPrevious = () => {
    if (audioElement && audioElement.currentTime > 3) {
      audioElement.currentTime = 0;
      return;
    }

    if (currentTrackIndex > 0) {
      currentTrackIndex -= 1;
      void loadTrack(true);
    } else {
      if (audioElement) {
        audioElement.currentTime = 0;
      }
    }
  };

  const handleSeekInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const value = Number(target.value);
    progress = clamp(value, 0, 100);

    if (!audioElement || !audioElement.duration) {
      displayedTime = (progress / 100) * currentTrack.duration;
      return;
    }

    const seekTo = (progress / 100) * audioElement.duration;
    displayedTime = seekTo;

    if (!isSeeking) {
      audioElement.currentTime = seekTo;
    }
  };

  const commitSeek = (event: Event) => {
    if (!audioElement) return;

    isSeeking = false;
    const target = event.target as HTMLInputElement;
    const value = Number(target.value);
    const ratio = clamp(value, 0, 100) / 100;

    if (audioElement.duration) {
      audioElement.currentTime = ratio * audioElement.duration;
    } else {
      audioElement.currentTime = ratio * currentTrack.duration;
    }

    if (isPlaying) {
      void audioElement.play();
    }
  };

  onMount(() => {
    void loadTrack(false);
  });
</script>

<section class="player">
  <div class="player__content">
    <header class="player__header">
      <h1>{$t('player.title')}</h1>
      <p>{$t('player.description')}</p>
    </header>

    <div class="player__now-playing" aria-live="polite">
      <h2>{$t('player.now_playing')}</h2>
      <p class="player__track-title">{$t(currentTrack.titleKey)}</p>
      <p class="player__track-duration">
        {$t('player.duration', {
          values: {
            elapsed: formatTime(displayedTime),
            total: formatTime(totalDuration),
            remaining: formatTime(Math.max(totalDuration - displayedTime, 0))
          }
        })}
      </p>
    </div>

    <div class="player__controls">
      <button
        class="player__control"
        type="button"
        on:click={playPrevious}
        aria-label={$t('player.previous_track')}
      >
        ◀◀
      </button>
      <button
        class="player__control player__control--primary"
        type="button"
        on:click={togglePlayback}
        aria-pressed={isPlaying}
        aria-label={isPlaying ? $t('player.pause') : $t('player.play')}
      >
        {isPlaying ? $t('player.pause') : $t('player.play')}
      </button>
      <button
        class="player__control"
        type="button"
        on:click={playNext}
        aria-label={$t('player.next_track')}
      >
        ▶▶
      </button>
    </div>

    <div class="player__timeline">
      <label class="player__timeline-label" for="player-progress">
        {$t('player.seek_label')}
      </label>
      <input
        id="player-progress"
        class="player__slider"
        type="range"
        min="0"
        max="100"
        step="0.1"
        value={progress}
        on:input={handleSeekInput}
        on:change={commitSeek}
        on:mousedown={() => (isSeeking = true)}
        on:touchstart={() => (isSeeking = true)}
        on:mouseup={commitSeek}
        on:touchend={commitSeek}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={Math.round(progress)}
        aria-valuetext={`${formatTime(displayedTime)} / ${formatTime(totalDuration)}`}
      />
      <div class="player__timeline-times" aria-hidden="true">
        <span>{formatTime(displayedTime)}</span>
        <span>{formatTime(Math.max(totalDuration - displayedTime, 0))}</span>
      </div>
    </div>

    <div class="player__playlist">
      <h2>{$t('player.track_list')}</h2>
      <ul>
        {#each tracks as track, index}
          <li>
            <button
              type="button"
              class:player__track-button--active={index === currentTrackIndex}
              class="player__track-button"
              on:click={() => playTrackAt(index)}
              aria-current={index === currentTrackIndex ? 'true' : 'false'}
              aria-label={$t('player.select_track', { values: { title: $t(track.titleKey) } })}
            >
              <span>{$t(track.titleKey)}</span>
              <span>{formatTime(track.duration)}</span>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  </div>

  <audio
    bind:this={audioElement}
    on:loadedmetadata={updateProgressFromAudio}
    on:timeupdate={() => {
      if (!isSeeking) {
        updateProgressFromAudio();
      }
    }}
    on:play={() => (isPlaying = true)}
    on:pause={() => (isPlaying = false)}
    on:ended={playNext}
    preload="metadata"
  ></audio>
</section>

<style>
  .player {
    padding: 2rem 1.5rem 3rem;
    display: flex;
    justify-content: center;
  }

  .player__content {
    width: min(960px, 100%);
    background: #0f172a;
    color: #f8fafc;
    border-radius: 1.5rem;
    padding: 2.5rem;
    box-shadow: 0 2rem 4rem rgba(15, 23, 42, 0.35);
  }

  .player__header h1 {
    margin: 0 0 0.5rem;
    font-size: clamp(1.75rem, 2.5vw, 2.5rem);
  }

  .player__header p {
    margin: 0 0 2rem;
    color: rgba(226, 232, 240, 0.8);
  }

  .player__now-playing {
    background: rgba(30, 41, 59, 0.9);
    padding: 1.5rem 2rem;
    border-radius: 1.25rem;
    margin-bottom: 2rem;
  }

  .player__now-playing h2 {
    margin: 0 0 0.5rem;
    font-size: 1rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(148, 163, 184, 0.9);
  }

  .player__track-title {
    margin: 0;
    font-size: clamp(1.25rem, 2vw, 1.75rem);
    font-weight: 600;
  }

  .player__track-duration {
    margin: 0.5rem 0 0;
    color: rgba(226, 232, 240, 0.75);
  }

  .player__controls {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .player__control {
    background: rgba(30, 41, 59, 0.8);
    color: #f8fafc;
    border: none;
    border-radius: 9999px;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    cursor: pointer;
    transition: transform 0.15s ease, background 0.2s ease;
  }

  .player__control:hover,
  .player__control:focus {
    background: rgba(51, 65, 85, 0.95);
    transform: translateY(-1px);
    outline: none;
  }

  .player__control:focus-visible {
    outline: 3px solid rgba(148, 163, 184, 0.65);
    outline-offset: 3px;
  }

  .player__control--primary {
    background: #38bdf8;
    color: #0f172a;
    font-weight: 600;
    padding: 0.9rem 2.5rem;
    font-size: 1.05rem;
  }

  .player__timeline {
    margin-bottom: 2rem;
  }

  .player__timeline-label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: rgba(148, 163, 184, 0.9);
  }

  .player__slider {
    width: 100%;
    appearance: none;
    height: 0.5rem;
    border-radius: 9999px;
    background: rgba(71, 85, 105, 0.7);
    outline: none;
  }

  .player__slider::-webkit-slider-thumb {
    appearance: none;
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background: #38bdf8;
    border: 2px solid #0f172a;
    cursor: pointer;
  }

  .player__slider::-moz-range-thumb {
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background: #38bdf8;
    border: 2px solid #0f172a;
    cursor: pointer;
  }

  .player__timeline-times {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    color: rgba(148, 163, 184, 0.9);
  }

  .player__playlist h2 {
    margin: 0 0 1rem;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(148, 163, 184, 0.9);
  }

  .player__playlist ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 0.75rem;
  }

  .player__track-button {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(30, 41, 59, 0.75);
    border: none;
    border-radius: 1rem;
    padding: 1rem 1.5rem;
    color: inherit;
    cursor: pointer;
    transition: transform 0.15s ease, background 0.2s ease;
    font-size: 1rem;
  }

  .player__track-button span:last-child {
    font-variant-numeric: tabular-nums;
    color: rgba(148, 163, 184, 0.95);
  }

  .player__track-button:hover,
  .player__track-button:focus {
    background: rgba(51, 65, 85, 0.95);
    transform: translateY(-1px);
    outline: none;
  }

  .player__track-button:focus-visible {
    outline: 3px solid rgba(56, 189, 248, 0.7);
    outline-offset: 3px;
  }

  .player__track-button--active {
    background: #38bdf8;
    color: #0f172a;
    font-weight: 600;
  }

  @media (max-width: 720px) {
    .player__content {
      padding: 2rem;
    }

    .player__controls {
      flex-direction: column;
      gap: 0.75rem;
    }

    .player__control--primary {
      width: 100%;
    }
  }
</style>
