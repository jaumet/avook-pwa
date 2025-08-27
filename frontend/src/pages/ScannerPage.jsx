import React, { useState } from 'react';
import { useZxing } from 'react-zxing';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import { getDeviceId } from '../services/device';

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

        // Navigate to player page with the data
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
    <div>
      <h1>{t('scan_qr_title')}</h1>
      <video ref={ref} />
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
