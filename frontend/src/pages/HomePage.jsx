import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const HomePage = () => {
  const { t } = useTranslation();

  const pageStyle = {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
    justifyContent: 'center',
    alignItems: 'center',
    textAlign: 'center'
  };

  const footerStyle = {
    marginTop: 'auto',
    padding: '1rem',
    fontSize: '0.8rem'
  };

  return (
    <div style={pageStyle}>
      <main>
        <h1>{t('app_title')}</h1>
        <p>{t('app_subtitle')}</p>
        <Link to="/scan">
          <button>{t('scan_qr_button')}</button>
        </Link>
      </main>
      <footer style={footerStyle}>
        <Link to="/legal">Legal & Privacy</Link>
      </footer>
    </div>
  );
};

export default HomePage;
