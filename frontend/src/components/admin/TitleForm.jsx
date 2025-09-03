import React, { useState, useEffect } from 'react';
import api from '../../services/api';

function TitleForm({ onFinished, existingTitle }) {
  const [title, setTitle] = useState({
    slug: '',
    title: '',
    author: '',
    language: 'en',
    duration_sec: 0,
    status: 'draft',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (existingTitle) {
      setTitle(existingTitle);
    }
  }, [existingTitle]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTitle(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (existingTitle) {
        // Update existing title
        await api.put(`/api/v1/admin/titles/${existingTitle.id}`, title);
      } else {
        // Create new title
        await api.post('/api/v1/admin/titles', title);
      }
      onFinished();
    } catch (err) {
      setError('Failed to save title.');
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
      <h3>{existingTitle ? 'Edit Title' : 'Create New Title'}</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input name="slug" value={title.slug} onChange={handleChange} placeholder="Slug" required />
      <input name="title" value={title.title} onChange={handleChange} placeholder="Title" required />
      <input name="author" value={title.author} onChange={handleChange} placeholder="Author" />
      <input name="language" value={title.language} onChange={handleChange} placeholder="Language (2 chars)" maxLength="2" />
      <input name="duration_sec" type="number" value={title.duration_sec} onChange={handleChange} placeholder="Duration (seconds)" />
      <select name="status" value={title.status} onChange={handleChange}>
        <option value="draft">Draft</option>
        <option value="published">Published</option>
        <option value="archived">Archived</option>
      </select>
      <button type="submit">Save Title</button>
    </form>
  );
}

export default TitleForm;
