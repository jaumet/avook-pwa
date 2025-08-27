import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div>
      <h1>Avook</h1>
      <p>Your personal audiobook player.</p>
      <Link to="/scan">
        <button>Scan QR Code</button>
      </Link>
    </div>
  );
};

export default HomePage;
