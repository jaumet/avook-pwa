import React, { useState, useEffect } from 'react';
import api from '../../services/api';

function BatchRow({ batch, onUploadSuccess }) {
  const [qrcodes, setQrcodes] = useState([]);
  const [showQRs, setShowQRs] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const fetchQRs = async () => {
    const response = await api.get(`/api/v1/admin/batches/${batch.id}/qrcodes`);
    const enriched = await Promise.all(
      response.data.map(async qr => {
        if (qr.image_path) {
          const jsonPath = qr.image_path.replace(/\.png$/, '.json');
          const jsonUrl = `${import.meta.env.VITE_S3_PUBLIC_URL}/${jsonPath}`;
          try {
            const metaRes = await fetch(jsonUrl);
            const meta = await metaRes.json();
            return { ...qr, pin: meta.pin, jsonUrl };
          } catch {
            return { ...qr, pin: null, jsonUrl };
          }
        }
        return { ...qr, pin: null };
      })
    );
    setQrcodes(enriched);
  };

  const toggleShowQRs = async () => {
    if (!showQRs) {
      await fetchQRs();
    }
    setShowQRs(!showQRs);
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploadStatus('Uploading...');
    try {
      const response = await api.post(`/api/v1/admin/batches/${batch.id}/upload-qrs`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setUploadStatus(response.data.message || 'Upload successful!');
      setSelectedFile(null);
      if (showQRs) {
        await fetchQRs();
      }
      onUploadSuccess();
    } catch (err) {
      setUploadStatus('Upload failed: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  return (
    <>
      <tr>
        <td>{batch.id}</td>
        <td>{batch.name}</td>
        <td>{batch.size}</td>
        <td>{batch.printed_at ? new Date(batch.printed_at).toLocaleString() : 'N/A'}</td>
        <td>
          <button onClick={toggleShowQRs}>{showQRs ? 'Hide' : 'Show'} QRs</button>
          <div>
            <input type="file" accept=".zip" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={!selectedFile}>Upload ZIP</button>
            {uploadStatus && <p>{uploadStatus}</p>}
          </div>
        </td>
      </tr>
      {showQRs && (
        <tr>
          <td colSpan="5">
            <h4>QR Codes for Batch {batch.id}</h4>
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th>Image</th>
                  <th>QR Code</th>
                  <th>Pin</th>
                  <th>State</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {qrcodes.map(qr => {
                  const imageUrl = qr.image_path ? `${import.meta.env.VITE_S3_PUBLIC_URL}/${qr.image_path}` : null;
                  return (
                    <tr key={qr.id}>
                      <td>
                        {imageUrl ?
                          <img src={imageUrl} alt={qr.qr} style={{ width: '100px', height: '100px' }} /> :
                          'No Image'
                        }
                      </td>
                      <td>
                        {qr.jsonUrl ? (
                          <a href={qr.jsonUrl} target="_blank" rel="noopener noreferrer">{qr.qr}</a>
                        ) : qr.qr}
                      </td>
                      <td>{qr.pin ?? 'N/A'}</td>
                      <td>{qr.state}</td>
                      <td>{new Date(qr.created_at).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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

  const [batchName, setBatchName] = useState('');

  useEffect(() => {
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

  const fetchBatches = React.useCallback(async () => {
    if (!selectedProductId) {
      setBatches([]);
      return;
    }
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/admin/products/${selectedProductId}/batches`);
      setBatches(response.data);
    } catch (err) {
      setError('Failed to fetch batches.');
    } finally {
      setLoading(false);
    }
  }, [selectedProductId]);

  useEffect(() => {
    fetchBatches();
  }, [fetchBatches]);

  const handleCreateBatch = async (e) => {
    e.preventDefault();
    if (!selectedProductId) {
      setError('Please select a product first.');
      return;
    }
    try {
      await api.post(
        `/api/v1/admin/products/${selectedProductId}/batches`,
        { name: batchName, size: 0 }
      );
      setBatchName('');
      await fetchBatches();
      setError('');
    } catch (err) {
      setError('Failed to create batch. ' + (err.response?.data?.detail || ''));
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
            <button type="submit">Create Batch</button>
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {batches.map(batch => (
                <BatchRow key={batch.id} batch={batch} onUploadSuccess={fetchBatches} />
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
