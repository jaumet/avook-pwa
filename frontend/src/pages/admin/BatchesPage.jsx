import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';

function BatchRow({ batch }) {
  const [qrcodes, setQrcodes] = useState([]);
  const [showQRs, setShowQRs] = useState(false);

  const toggleShowQRs = async () => {
    if (!showQRs) {
      const response = await api.get(`/api/v1/admin/batches/${batch.id}/qrcodes`);
      setQrcodes(response.data);
    }
    setShowQRs(!showQRs);
  };

  return (
    <>
      <tr>
        <td>{batch.id}</td>
        <td>{batch.name}</td>
        <td>{batch.size}</td>
        <td>{batch.printed_at ? new Date(batch.printed_at).toLocaleString() : 'N/A'}</td>
        <td><button onClick={toggleShowQRs}>{showQRs ? 'Hide' : 'Show'} QRs</button></td>
      </tr>
      {showQRs && (
        <tr>
          <td colSpan="5">
            <ul>
              {qrcodes.map(qr => (
                <li key={qr.id}>
                  <Link to={`/admin/qrcodes/${qr.qr}`}>{qr.qr}</Link> ({qr.state})
                </li>
              ))}
            </ul>
          </td>
        </tr>
      )}
    </>
  );
}

function BatchesPage() {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Form state for creating a new batch
  const [batchName, setBatchName] = useState('');
  const [quantity, setQuantity] = useState(10);

  useEffect(() => {
    // Fetch all products for the selection dropdown
    const fetchProducts = async () => {
      try {
        const response = await api.get('/api/v1/admin/products');
        setProducts(response.data);
      } catch (err) {
        setError('Failed to fetch products.');
      }
    };
    fetchProducts();
  }, []);

  useEffect(() => {
    // Fetch batches when a product is selected
    if (!selectedProductId) {
      setBatches([]);
      return;
    }
    const fetchBatches = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/api/v1/admin/products/${selectedProductId}/batches`);
        setBatches(response.data);
      } catch (err) {
        setError('Failed to fetch batches.');
      } finally {
        setLoading(false);
      }
    };
    fetchBatches();
  }, [selectedProductId]);

  const handleCreateBatch = async (e) => {
    e.preventDefault();
    if (!selectedProductId) {
      setError('Please select a product first.');
      return;
    }
    try {
      const response = await api.post(
        `/api/v1/admin/products/${selectedProductId}/batches`,
        { name: batchName, quantity: quantity },
        { responseType: 'blob' } // Important to handle the file download
      );
      // Create a blob from the response and trigger download
      const blob = new Blob([response.data], { type: 'text/csv' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `qrcodes_batch_${new Date().getTime()}.csv`;
      link.click();

      // Clear form and refetch batches
      setBatchName('');
      setQuantity(10);
      // Refetch batches for the current product
      const refetchResponse = await api.get(`/api/v1/admin/products/${selectedProductId}/batches`);
      setBatches(refetchResponse.data);

    } catch (err) {
      setError('Failed to create batch.');
    }
  };

  return (
    <div>
      <h1>Batches & QR Code Generation</h1>

      <select value={selectedProductId} onChange={e => setSelectedProductId(e.target.value)}>
        <option value="">-- Select a Product --</option>
        {products.map(p => <option key={p.id} value={p.id}>{p.title.title} - {p.sku_ean}</option>)}
      </select>

      {selectedProductId && (
        <div>
          <form onSubmit={handleCreateBatch} style={{ margin: '2rem 0' }}>
            <h3>Create New Batch for Selected Product</h3>
            <input type="text" value={batchName} onChange={e => setBatchName(e.target.value)} placeholder="Batch Name" required />
            <input type="number" value={quantity} onChange={e => setQuantity(parseInt(e.target.value, 10))} placeholder="Quantity" min="1" required />
            <button type="submit">Generate QR Codes (CSV)</button>
          </form>

          <h2>Existing Batches</h2>
          {loading && <p>Loading batches...</p>}
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Size</th>
                <th>Printed At</th>
                <th>QR Codes</th>
              </tr>
            </thead>
            <tbody>
              {batches.map(batch => (
                <BatchRow key={batch.id} batch={batch} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default BatchesPage;
