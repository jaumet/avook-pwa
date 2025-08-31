import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import { BrowserMultiFormatReader } from '@zxing/browser';

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [useNative, setUseNative] = useState(false);
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const zxingReaderRef = useRef(null);

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
      if (zxingReaderRef.current) {
        zxingReaderRef.current.reset();
        zxingReaderRef.current = null;
      }
    };

    const startScanner = async () => {
      try {
        const devices = await BrowserMultiFormatReader.listVideoInputDevices();
        const deviceId = devices[0]?.deviceId;

        if ('BarcodeDetector' in window) {
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

        videoRef.current.style.display = 'block';
        zxingReaderRef.current = new BrowserMultiFormatReader();
        await zxingReaderRef.current.decodeFromVideoDevice(
          deviceId,
          videoRef.current,
          (result, err) => {
            if (result) {
              stop();
              handleResult(result.getText());
            }
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
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;