import React, { useEffect, useRef } from 'react';
import Hls from 'hls.js';

const HLSPlayer = ({ src, title, author }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hls;

    if (Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play();
      });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // For Safari and other browsers that support HLS natively
      video.src = src;
      video.addEventListener('loadedmetadata', () => {
        video.play();
      });
    }

    // MediaSession API
    if ('mediaSession' in navigator) {
      navigator.mediaSession.metadata = new window.MediaMetadata({
        title: title,
        artist: author,
        album: 'Avook Audiobook',
      });

      navigator.mediaSession.setActionHandler('play', () => video.play());
      navigator.mediaSession.setActionHandler('pause', () => video.pause());
    }

    return () => {
      if (hls) {
        hls.destroy();
      }
    };
  }, [src, title, author]);

  return <video ref={videoRef} controls style={{ width: '100%' }} />;
};

export default HLSPlayer;
