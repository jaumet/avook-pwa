import React from 'react';
import { useLocation, useParams } from 'react-router-dom';
import HLSPlayer from '../components/HLSPlayer';

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
      <h1>{authData.title}</h1>
      <p>by {authData.author}</p>
      <HLSPlayer
        src={authData.signed_url}
        title={authData.title}
        author={authData.author}
      />
      <p>Starts at: {authData.start_position} seconds</p>
    </div>
  );
};

export default PlayerPage;
