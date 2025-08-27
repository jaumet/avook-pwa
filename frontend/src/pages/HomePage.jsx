import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const HomePage = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('app_title')}</h1>
      <p>{t('app_subtitle')}</p>
      <Link to="/scan">
        <button>{t('scan_qr_button')}</button>
      </Link>
    </div>
  );
};

export default HomePage;
