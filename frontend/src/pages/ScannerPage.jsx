import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import { Html5Qrcode } from 'html5-qrcode';

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const html5QrRef = useRef(null);

  const handleResult = useCallback(async (qrCode) => {
    setError('');
    try {
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
      const qrRegion = document.getElementById('qr-reader');
      if (qrRegion) qrRegion.style.display = 'none';
    };

    const startScanner = async () => {
      try {
        const cameras = await Html5Qrcode.getCameras();
        const deviceId = cameras[0]?.id;

        const qrRegion = document.getElementById('qr-reader');

        if ('BarcodeDetector' in window) {
          streamRef.current = await navigator.mediaDevices.getUserMedia({
            video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' }
          });
          if (qrRegion) qrRegion.style.display = 'none';
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
        if (qrRegion) qrRegion.style.display = 'block';
        videoRef.current.style.display = 'none';
        html5QrRef.current = new Html5Qrcode('qr-reader');
        await html5QrRef.current.start(
          { deviceId: { exact: deviceId } },
          { fps: 10, qrbox: 250 },
          (decodedText) => {
            stop();
            handleResult(decodedText);
          }
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
      <div
        id="qr-reader"
        style={{ width: '100%', maxWidth: '500px', margin: '0 auto', display: 'none' }}
      />
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
