import React, { useState, useEffect } from 'react';
import api from '../../services/api';

function ProductForm({ onFinished, existingProduct }) {
  const [product, setProduct] = useState({
    title_id: '',
    sku_ean: '',
    price_cents: 0,
    notes: '',
  });
  const [titles, setTitles] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch titles for the dropdown
    const fetchTitles = async () => {
      try {
        const response = await api.get('/api/v1/admin/titles');
        setTitles(response.data);
        // Set a default title_id if creating a new product
        if (!existingProduct && response.data.length > 0) {
          setProduct(p => ({ ...p, title_id: response.data[0].id }));
        }
      } catch (err) {
        console.error("Failed to fetch titles", err);
        setError("Could not load titles for selection.");
      }
    };
    fetchTitles();
  }, [existingProduct]);

  useEffect(() => {
    if (existingProduct) {
      setProduct({
        title_id: existingProduct.title_id,
        sku_ean: existingProduct.sku_ean || '',
        price_cents: existingProduct.price_cents || 0,
        notes: existingProduct.notes || '',
      });
    }
  }, [existingProduct]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProduct(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!product.title_id) {
        setError('Please select a title.');
        return;
    }
    try {
      if (existingProduct) {
        await api.put(`/api/v1/admin/products/${existingProduct.id}`, product);
      } else {
        await api.post('/api/v1/admin/products', product);
      }
      onFinished();
    } catch (err) {
      setError('Failed to save product.');
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
      <h3>{existingProduct ? 'Edit Product' : 'Create New Product'}</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <select name="title_id" value={product.title_id} onChange={handleChange} required>
        <option value="">Select a Title</option>
        {titles.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
      </select>

      <input name="sku_ean" value={product.sku_ean} onChange={handleChange} placeholder="SKU/EAN" />
      <input name="price_cents" type="number" value={product.price_cents} onChange={handleChange} placeholder="Price (cents)" />
      <textarea name="notes" value={product.notes} onChange={handleChange} placeholder="Notes" />

      <button type="submit">Save Product</button>
    </form>
  );
}

export default ProductForm;
