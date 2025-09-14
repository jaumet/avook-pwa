import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Html5Qrcode } from 'html5-qrcode';

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [scannedUrl, setScannedUrl] = useState('');
  const [exists, setExists] = useState(null);
  const qrRef = useRef(null);
  const html5QrRef = useRef(null);

  const handleResult = useCallback(async (text) => {
    setError('');
    setExists(null);
    setScannedUrl('');
    try {
      const url = new URL(text);
      setScannedUrl(url.toString());
      try {
        const res = await fetch(url.toString(), { method: 'HEAD' });
        setExists(res.ok);
      } catch {
        setExists(false);
      }
    } catch {
      setError(t('error_invalid_qr'));
    }
  }, [t]);

  useEffect(() => {
    const start = async () => {
      try {
        const cameras = await Html5Qrcode.getCameras();
        const deviceId = cameras.find(c => /back|rear|environment/i.test(c.label))?.id || cameras[0]?.id;
        html5QrRef.current = new Html5Qrcode(qrRef.current);
        await html5QrRef.current.start(
          deviceId || { facingMode: 'environment' },
          { fps: 10, qrbox: 250 },
          (decodedText) => {
            html5QrRef.current.stop().catch(() => {});
            html5QrRef.current.clear();
            handleResult(decodedText);
          }
        );
      } catch (err) {
        console.error('Unable to start scanning.', err);
        setError(t('error_scanner'));
      }
    };
    start();
    return () => {
      html5QrRef.current?.stop().catch(() => {});
      html5QrRef.current?.clear();
    };
  }, [handleResult, t]);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>{t('scan_qr_title')}</h1>
      <div id="qr-reader" ref={qrRef} style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }} />
      {exists && scannedUrl && (
        <p>
          {t('qr_exists_message')}{' '}
          <a href={scannedUrl} target="_blank" rel="noopener noreferrer">{scannedUrl}</a>
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
