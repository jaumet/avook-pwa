
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Html5Qrcode } from 'html5-qrcode';

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [scannedUrl, setScannedUrl] = useState('');
  const [exists, setExists] = useState(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const html5QrRef = useRef(null);
  const handleResult = useCallback((qrCode) => {
    setError('');
    setExists(null);
    setScannedUrl('');
    console.log('QR detected:', qrCode);
    try {
      const url = new URL(qrCode);
      setScannedUrl(url.toString());
      fetch(url.toString(), { method: 'HEAD' })
        .then((res) => {
          setExists(res.ok);
        })
        .catch(() => {
          setExists(false);
        });
    } catch (err) {
      setError(t('error_invalid_qr'));
    }
  }, [t]);

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
        const deviceId = cameras.find(c =>
          /back|rear|environment/i.test(c.label)
        )?.id || cameras[0]?.id;

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
        const cameraConfig = deviceId || { facingMode: 'environment' };
        await html5QrRef.current.start(
          cameraConfig,
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
      {exists && scannedUrl && (
        <p>
          {t('qr_exists_message')}{' '}
          <a href={scannedUrl} target="_blank" rel="noopener noreferrer">
            {scannedUrl}
          </a>
        </p>
      )}
      {exists === false && (
        <p style={{ color: 'red' }}>{t('qr_not_found_message')}</p>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
