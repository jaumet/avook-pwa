import React from 'react';
import { useLocation, useParams } from 'react-router-dom';

const PlayerPage = () => {
  const { qr } = useParams();
  const location = useLocation();
  const authData = location.state?.authData;

  if (!authData) {
    return (
      <div>
        <h1>Error</h1>
        <p>No authorization data found. Please scan a QR code again.</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Player for QR: {qr}</h1>
      <p><strong>Signed URL:</strong> {authData.signed_url}</p>
      <p><strong>Start Position:</strong> {authData.start_position} seconds</p>
      {/* HLS player will be implemented here in a later step */}
    </div>
  );
};

export default PlayerPage;
