import React from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import HLSPlayer from '../components/HLSPlayer';

import { getDeviceId } from '../services/device';
import { useEffect, useState } from 'react';

const PlayerPage = () => {
  const { t } = useTranslation();
  const { qr } = useParams();
  const location = useLocation();
  const authData = location.state?.authData;
  const [deviceId, setDeviceId] = useState(null);

  useEffect(() => {
    getDeviceId().then(setDeviceId);
  }, []);

  if (!authData) {
    return (
      <div>
        <h1>{t('error_title', 'Error')}</h1>
        <p>{t('error_no_auth')}</p>
      </div>
    );
  }

  return (
    <div>
      <h1>{authData.title}</h1>
      <p>by {authData.author}</p>
      {deviceId && (
        <HLSPlayer
          src={authData.signed_url}
          title={authData.title}
          author={authData.author}
          qr={qr}
          deviceId={deviceId}
        />
      )}
      <p>{t('player_starts_at', { seconds: authData.start_position })}</p>
    </div>
  );
};

export default PlayerPage;
