import React from 'react';

function LegalPage() {
  const containerStyle = {
    padding: '2rem',
    fontFamily: 'sans-serif',
    lineHeight: '1.6',
  };

  return (
    <div style={containerStyle}>
      <h1>Legal & Privacy Policy</h1>

      <h2>Privacy Policy</h2>
      <p>
        This privacy policy will help you understand how our application uses and protects the data you provide to us when you visit and use it.
      </p>

      <h3>What User Data We Collect</h3>
      <p>
        We do not collect any Personally Identifiable Information (PII) from end-users of the audiobooks. Our service is designed to be anonymous.
      </p>
      <p>
        When you activate an audiobook with a QR code, we only store the following non-personal information:
      </p>
      <ul>
        <li>A unique, anonymous identifier for your device.</li>
        <li>The QR code you scanned.</li>
        <li>Your listening progress (which chapter and position) to allow you to resume playback.</li>
      </ul>

      <h3>Why We Collect Your Data</h3>
      <p>
        We are collecting this anonymous data for the sole purpose of providing and improving the audiobook playback service, specifically:
      </p>
      <ul>
        <li>To allow you to resume listening where you left off.</li>
        <li>To enforce the limit of active devices per QR code.</li>
      </ul>

      <h3>Data Security</h3>
      <p>
        We are committed to securing your anonymous data and keeping it confidential.
      </p>

      <h2>General Data Protection Regulation (GDPR)</h2>
      <p>
        As we do not collect personal data from end-users, our service is compliant with the GDPR's principles of data minimization and privacy by design. The anonymous device identifier and progress data are essential for the functioning of the service and are not used for any other purpose.
      </p>
    </div>
  );
}

export default LegalPage;
