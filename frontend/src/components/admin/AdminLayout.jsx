import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import useAdminAuthStore from '../../services/adminAuth';

function AdminLayout() {
  const logout = useAdminAuthStore(state => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  // A simple layout with a sidebar and a main content area
  return (
    <div style={{ display: 'flex' }}>
      <nav style={{ width: '200px', borderRight: '1px solid #ccc', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
        <div>
          <h2>Admin Menu</h2>
          <ul>
            <li><Link to="/admin">Dashboard</Link></li>
            <li><Link to="/admin/users">Users</Link></li>
            <li><Link to="/admin/titles">Titles</Link></li>
            <li><Link to="/admin/products">Products</Link></li>
            <li><Link to="/admin/batches">Batches & QR</Link></li>
          </ul>
        </div>
        <div style={{ marginTop: 'auto' }}>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main style={{ flex: 1, padding: '1rem' }}>
        <Outlet /> {/* This will render the nested route's component */}
      </main>
    </div>
  );
}

export default AdminLayout;
