import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';

function QRDetailPage() {
  const { qr } = useParams();
  const [qrDetails, setQrDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDetails = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/admin/qrcodes/${qr}`);
      setQrDetails(response.data);
    } catch (err) {
      setError('Failed to fetch QR code details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [qr]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset this QR code? This will remove all linked devices.')) {
      try {
        await api.post(`/api/v1/admin/qrcodes/${qr}/reset`);
        alert('QR Code reset successfully.');
        fetchDetails(); // Refresh details
      } catch (err) {
        setError('Failed to reset QR code.');
        console.error(err);
      }
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!qrDetails) return <div>No details found for this QR code.</div>;

  return (
    <div>
      <h1>QR Code Details: {qrDetails.qr}</h1>
      <p><strong>State:</strong> {qrDetails.state}</p>
      <p><strong>Product ID:</strong> {qrDetails.product_id}</p>
      <p><strong>Batch ID:</strong> {qrDetails.batch_id}</p>
      <button onClick={handleReset}>Reset QR Code</button>

      <h2>Device Bindings</h2>
      {qrDetails.device_bindings.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Device ID</th>
              <th>Created At</th>
              <th>Last Seen At</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {qrDetails.device_bindings.map(binding => (
              <tr key={binding.id}>
                <td>{binding.device_id}</td>
                <td>{new Date(binding.created_at).toLocaleString()}</td>
                <td>{binding.last_seen_at ? new Date(binding.last_seen_at).toLocaleString() : 'N/A'}</td>
                <td>{binding.active ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No devices are bound to this QR code.</p>
      )}
    </div>
  );
}

export default QRDetailPage;
