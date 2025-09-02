import React, { useState, useEffect } from 'react';
import api from '../../services/api';

function TitlesPage() {
  const [titles, setTitles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    const fetchTitles = async () => {
      try {
        const response = await api.get('/api/v1/admin/titles');
        setTitles(response.data);
      } catch (err) {
        setError('Failed to fetch titles.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTitles();
  }, []);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async (titleId) => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await api.post(`/api/v1/admin/titles/${titleId}/upload-cover`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      // Update the title in the list with the new cover path
      setTitles(titles.map(t => t.id === titleId ? response.data : t));
      alert('Upload successful!');
    } catch (err) {
      setError('Failed to upload cover.');
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h1>Titles Management</h1>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>Cover Path</th>
            <th>Upload Cover</th>
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
                <input type="file" onChange={handleFileChange} />
                <button onClick={() => handleUpload(title.id)}>Upload</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TitlesPage;
