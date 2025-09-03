import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import TitleForm from '../../components/admin/TitleForm';

function TitlesPage() {
  const [titles, setTitles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingTitle, setEditingTitle] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  const fetchTitles = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/admin/titles');
      setTitles(response.data);
    } catch (err) {
      setError('Failed to fetch titles.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTitles();
  }, [fetchTitles]);

  const handleFormFinished = () => {
    setEditingTitle(null);
    setIsCreating(false);
    fetchTitles(); // Refetch all titles
  };

  const handleDelete = async (titleId) => {
    if (window.confirm('Are you sure you want to delete this title?')) {
      try {
        await api.delete(`/api/v1/admin/titles/${titleId}`);
        fetchTitles(); // Refetch
      } catch (err) {
        setError('Failed to delete title.');
        console.error(err);
      }
    }
  };

  const handleUpload = async (titleId, file) => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/api/v1/admin/titles/${titleId}/upload-cover`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      fetchTitles(); // Refetch to show new cover path
    } catch (err) {
      setError('Failed to upload cover.');
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  if (isCreating || editingTitle) {
    return (
      <div>
        <button onClick={() => { setIsCreating(false); setEditingTitle(null); }}>Back to List</button>
        <TitleForm onFinished={handleFormFinished} existingTitle={editingTitle} />
      </div>
    );
  }

  return (
    <div>
      <h1>Titles Management</h1>
      <button onClick={() => setIsCreating(true)}>Create New Title</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>Cover Path</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {titles.map((title) => (
            <tr key={title.id}>
              <td>{title.id}</td>
              <td>{title.title}</td>
              <td>{title.author}</td>
              <td>{title.cover_path}</td>
              <td>
                <button onClick={() => setEditingTitle(title)}>Edit</button>
                <button onClick={() => handleDelete(title.id)}>Delete</button>
                <input type="file" onChange={(e) => handleUpload(title.id, e.target.files[0])} style={{ display: 'block', marginTop: '5px' }} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TitlesPage;
