import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import { Html5Qrcode } from 'html5-qrcode';

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [useNative, setUseNative] = useState(false);
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const html5QrRef = useRef(null);
  const regionId = 'html5qr-code-region';

  const handleResult = useCallback(async (qrCode) => {
    setError('');
    try {
      let extractedCode = null;
      try {
        const url = new URL(qrCodeUrl);
        const match = url.pathname.match(/\/code\/([^\/]+)/) || url.pathname.match(/\/share\/([^\/]+)/);
        if (match && match[1]) {
          extractedCode = match[1];
        }
      } catch (e) {
        // Not a valid URL, maybe the QR code is the code itself
        extractedCode = qrCodeUrl;
      }

      if (!extractedCode) {
        setError(t('error_invalid_qr'));
        return;
      }

      const deviceId = await getDeviceId();
      const baseFromEnv = import.meta.env.VITE_API_BASE;
      const fallbackBase = window.location.port === '5173' ? 'http://localhost:8000' : '';
      const apiBase = (baseFromEnv || fallbackBase).replace(/\/$/, '');
      const slug = qrCode.trim().split('/').pop();
      const url = `${apiBase}/api/v1/abook/${slug}/play-auth`;
      const response = await axios.get(url, {
        params: { device_id: deviceId }
      });
      navigate(`/play/${slug}`, { state: { authData: response.data } });
    } catch (err) {
      console.error('API Error:', err);
      if (err.response) {
        setError(err.response.data.detail || t('error_auth_failed'));
      } else {
        setError(t('error_network'));
      }
    }
  }, [navigate, t]);

  useEffect(() => {
    const stop = () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (html5QrRef.current) {
        html5QrRef.current.stop().catch(() => {});
        html5QrRef.current.clear();
        html5QrRef.current = null;
      }
    };

    const startScanner = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        const deviceId = videoDevices[0]?.deviceId;

        if ('BarcodeDetector' in window) {
          const regionEl = document.getElementById(regionId);
          if (regionEl) regionEl.style.display = 'none';
          streamRef.current = await navigator.mediaDevices.getUserMedia({
            video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' }
          });
          videoRef.current.style.display = 'block';
          videoRef.current.srcObject = streamRef.current;
          await videoRef.current.play();

          const formats = await window.BarcodeDetector.getSupportedFormats();
          if (formats.includes('qr_code')) {
            const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
            const scan = async () => {
              try {
                if (videoRef.current.readyState < videoRef.current.HAVE_ENOUGH_DATA) {
                  animationRef.current = requestAnimationFrame(scan);
                  return;
                }
                const barcodes = await detector.detect(videoRef.current);
                if (barcodes.length) {
                  stop();
                  handleResult(barcodes[0].rawValue);
                  return;
                }
              } catch (e) {
                // ignore detection errors
              }
              animationRef.current = requestAnimationFrame(scan);
            };
            animationRef.current = requestAnimationFrame(scan);
            return;
          }
        }

        videoRef.current.style.display = 'none';
        html5QrRef.current = new Html5Qrcode(regionId);
        await html5QrRef.current.start(
          deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' },
          { fps: 10, qrbox: 250 },
          (text) => {
            stop();
            handleResult(text);
          },
          undefined
        );
      } catch (err) {
        setError(t('error_scanner'));
        console.error('Unable to start scanning.', err);
      }
    };

    startScanner();

    return stop;
  }, [handleResult, t]);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>{t('scan_qr_title')}</h1>
      <video
        ref={videoRef}
        style={{ width: '100%', maxWidth: '500px', margin: '0 auto', display: 'none' }}
      />
      <div id={regionId} style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }} />
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
