import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';

const qrcodeRegionId = "html5qr-code-full-region";

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [useNative, setUseNative] = useState(false);
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const useNativeRef = useRef(false);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const html5QrCodeRef = useRef(null);

  const handleResult = useCallback(async (qrCodeUrl) => {
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
      const apiBase = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
      const url = `${apiBase}/api/v1/abook/${qrCode}/play-auth`;
      const response = await axios.get(url, {
        params: { device_id: deviceId }
      });
      navigate(`/play/${extractedCode}`, { state: { authData: response.data } });
    } catch (err) {
      console.error("API Error:", err);
      if (err.response) {
        setError(err.response.data.detail || t('error_auth_failed'));
      } else {
        setError(t('error_network'));
      }
    }
  }, [navigate, t]);

  useEffect(() => {
    const stopNative = () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };

    const startScanner = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        const deviceId = videoDevices[0]?.deviceId;

        if ('BarcodeDetector' in window) {
          const formats = await window.BarcodeDetector.getSupportedFormats();
          if (formats.includes('qr_code')) {
            useNativeRef.current = true;
            setUseNative(true);
            streamRef.current = await navigator.mediaDevices.getUserMedia({
              video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' }
            });
            videoRef.current.srcObject = streamRef.current;
            await videoRef.current.play();
            const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
            const scan = async () => {
              try {
                const barcodes = await detector.detect(videoRef.current);
                if (barcodes.length) {
                  stopNative();
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

        html5QrCodeRef.current = new Html5Qrcode(qrcodeRegionId);
        await html5QrCodeRef.current.start(
          deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            rememberLastUsedCamera: true,
            formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE]
          },
          (decodedText) => {
            html5QrCodeRef.current
              .stop()
              .then(() => handleResult(decodedText))
              .catch(err => {
                console.error("Failed to stop scanner after success", err);
                handleResult(decodedText);
              });
          },
          () => {}
        );
      } catch (err) {
        setError(t('error_scanner'));
        console.error("Unable to start scanning.", err);
      }
    };

    startScanner();

    return () => {
      if (useNativeRef.current) {
        stopNative();
      } else if (html5QrCodeRef.current) {
        html5QrCodeRef.current.stop().catch(err => {
          console.error("Failed to stop scanner on cleanup", err);
        });
      }
    };
  }, [handleResult, t]);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>{t('scan_qr_title')}</h1>
      {useNative ? (
        <video
          ref={videoRef}
          style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }}
        />
      ) : (
        <div
          id={qrcodeRegionId}
          style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }}
        />
      )}
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
