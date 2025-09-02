import React from 'react';
import { Outlet, Link } from 'react-router-dom';

function AdminLayout() {
  // A simple layout with a sidebar and a main content area
  return (
    <div style={{ display: 'flex' }}>
      <nav style={{ width: '200px', borderRight: '1px solid #ccc', padding: '1rem' }}>
        <h2>Admin Menu</h2>
        <ul>
          <li><Link to="/admin">Dashboard</Link></li>
          <li><Link to="/admin/users">Users</Link></li>
          <li><Link to="/admin/titles">Titles</Link></li>
          <li><Link to="/admin/products">Products</Link></li>
        </ul>
      </nav>
      <main style={{ flex: 1, padding: '1rem' }}>
        <Outlet /> {/* This will render the nested route's component */}
      </main>
    </div>
  );
}

export default AdminLayout;
