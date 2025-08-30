import React, { useEffect, useRef } from 'react';
import Hls from 'hls.js';
import axios from 'axios';

const HLSPlayer = ({ src, title, author, qr, deviceId }) => {
  const videoRef = useRef(null);

  const syncProgress = async () => {
    if (!videoRef.current || !qr || !deviceId) return;
    const position = Math.round(videoRef.current.currentTime);
    const apiBase = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
    try {
      await axios.post(`${apiBase}/api/v1/abook/${qr}/progress`, {
        device_id: deviceId,
        position_sec: position,
      });
    } catch (error) {
      console.error("Failed to sync progress:", error);
    }
  };

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

    // Progress syncing
    const progressInterval = setInterval(syncProgress, 30000); // Sync every 30 seconds
    video.addEventListener('pause', syncProgress);

    return () => {
      if (hls) {
        hls.destroy();
      }
      clearInterval(progressInterval);
      video.removeEventListener('pause', syncProgress);
    };
  }, [src, title, author, qr, deviceId]);

  return <video ref={videoRef} controls style={{ width: '100%' }} />;
};

export default HLSPlayer;
