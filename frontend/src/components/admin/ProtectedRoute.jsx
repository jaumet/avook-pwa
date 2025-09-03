import React from 'react';
import { Navigate } from 'react-router-dom';
import useAdminAuthStore from '../../services/adminAuth';

function ProtectedRoute({ children }) {
  const { token } = useAdminAuthStore();

  if (!token) {
    // If no token, redirect to the login page
    return <Navigate to="/admin/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
