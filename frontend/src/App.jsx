import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ScannerPage from './pages/ScannerPage';
import PlayerPage from './pages/PlayerPage';
import RecoverPinPage from './pages/RecoverPinPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scan" element={<ScannerPage />} />
        <Route path="/play/:qr" element={<PlayerPage />} />
        <Route path="/recover" element={<RecoverPinPage />} />
      </Routes>
    </Router>
  );
}

export default App;
