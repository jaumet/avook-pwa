import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import ProductForm from '../../components/admin/ProductForm';

function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingProduct, setEditingProduct] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/admin/products');
      setProducts(response.data);
    } catch (err) {
      setError('Failed to fetch products.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleFormFinished = () => {
    setEditingProduct(null);
    setIsCreating(false);
    fetchProducts(); // Refetch all products
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await api.delete(`/api/v1/admin/products/${productId}`);
        fetchProducts(); // Refetch
      } catch (err) {
        setError('Failed to delete product.');
        console.error(err);
      }
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  if (isCreating || editingProduct) {
    return (
      <div>
        <button onClick={() => { setIsCreating(false); setEditingProduct(null); }}>Back to List</button>
        <ProductForm onFinished={handleFormFinished} existingProduct={editingProduct} />
      </div>
    );
  }

  return (
    <div>
      <h1>Products Management</h1>
      <button onClick={() => setIsCreating(true)}>Create New Product</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>SKU/EAN</th>
            <th>Price (cents)</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.id}</td>
              <td>{product.title.title}</td>
              <td>{product.sku_ean}</td>
              <td>{product.price_cents}</td>
              <td>
                <button onClick={() => setEditingProduct(product)}>Edit</button>
                <button onClick={() => handleDelete(product.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ProductsPage;
