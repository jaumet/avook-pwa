import React, { useState } from 'react';
import { useZxing } from 'react-zxing';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';

const scannerContainerStyle = {
  width: '100%',
  maxWidth: '500px',
  margin: '20px auto',
  position: 'relative',
  border: '1px solid #ccc',
};

const videoStyle = {
  width: '100%',
  height: 'auto',
  display: 'block',
};

const overlayStyle = {
  position: 'absolute',
  top: '0',
  left: '0',
  width: '100%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const targetBoxStyle = {
    width: '60%',
    height: '60%',
    border: '3px solid red',
    boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
    borderRadius: '8px',
};


const ScannerPage = () => {
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const { ref } = useZxing({
    async onResult(result) {
      setError('');
      const qrCode = result.getText();

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
    },
    onError(err) {
      console.error("Scanner Error:", err);
      setError(t('error_scanner'));
    }
  });

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>{t('scan_qr_title')}</h1>
      <div style={scannerContainerStyle}>
        <video ref={ref} style={videoStyle} />
        <div style={overlayStyle}>
            <div style={targetBoxStyle}></div>
        </div>
      </div>
      <p>Point your camera at a QR code.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
