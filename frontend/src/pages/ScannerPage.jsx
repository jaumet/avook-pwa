import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';

const qrcodeRegionId = "html5qr-code-full-region";

const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleResult = useCallback(async (qrCode) => {
    setError('');
    try {
      const deviceId = await getDeviceId();
      const apiUrl = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/v1/abook/${qrCode}/play-auth`, {
        params: { device_id: deviceId }
      });
      navigate(`/play/${qrCode}`, { state: { authData: response.data } });
    } catch (err) {
      console.error("API Error:", err);
      if (err.response) {
        setError(err.response.data.detail || t('error_auth_failed'));
      } else {
        setError('An unexpected error occurred.');
      }
    }
  }, [navigate, t]);

  useEffect(() => {
    // This effect will run only once on component mount.
    const html5QrCode = new Html5Qrcode(qrcodeRegionId);
    let isScannerStopped = false;

    const qrCodeSuccessCallback = (decodedText) => {
        if (!isScannerStopped) {
            isScannerStopped = true;
            html5QrCode.stop().then(() => {
                handleResult(decodedText);
            }).catch((err) => {
                console.error("Failed to stop scanner after success", err);
                handleResult(decodedText); // Proceed even if stop fails
            });
        }
    };

    const qrCodeErrorCallback = () => {
        // Frequent callback; avoid logging noise
    };

    const startScanner = async () => {
        try {
            const devices = await Html5Qrcode.getCameras();
            const deviceId = devices?.[0]?.id;
            await html5QrCode.start(
                deviceId ? { deviceId: { exact: deviceId } } : { facingMode: "environment" },
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 },
                    rememberLastUsedCamera: true,
                    experimentalFeatures: { useBarCodeDetectorIfSupported: true },
                    formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE]
                },
                qrCodeSuccessCallback,
                qrCodeErrorCallback
            );
        } catch (err) {
            setError(t('error_scanner'));
            console.error("Unable to start scanning.", err);
        }
    };

    startScanner();

    return () => {
        if (!isScannerStopped) {
            html5QrCode.stop().catch(err => {
                console.error("Failed to stop scanner on cleanup", err);
            });
        }
    };
  }, [handleResult, t]);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>{t('scan_qr_title')}</h1>
      <div id={qrcodeRegionId} style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }} />
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
