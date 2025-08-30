import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import jsQR from 'jsqr';
  const streamRef = useRef(null);
  const animationRef = useRef(null);
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
    const stop = () => {
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

        streamRef.current = await navigator.mediaDevices.getUserMedia({
          video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment' }
        });
        videoRef.current.srcObject = streamRef.current;
        await videoRef.current.play();

        if ('BarcodeDetector' in window) {
          const formats = await window.BarcodeDetector.getSupportedFormats();
          if (formats.includes('qr_code')) {
            const detector = new window.BarcodeDetector({ formats: ['qr_code'] });
            const scan = async () => {
              try {
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

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const scan = () => {
          if (!videoRef.current) return;
          canvas.width = videoRef.current.videoWidth;
          canvas.height = videoRef.current.videoHeight;
          context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
          const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          if (code) {
            stop();
            handleResult(code.data);
            return;
          }
          animationRef.current = requestAnimationFrame(scan);
        };
        animationRef.current = requestAnimationFrame(scan);
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
        style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }}
      />
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;