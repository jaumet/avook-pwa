import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import useAdminAuthStore from './adminAuth';
import api from './api';

const AuthVerify = () => {
  const location = useLocation();
  const { token, logout, user } = useAdminAuthStore.getState();

  useEffect(() => {
    const verifyToken = async () => {
      if (token && !user) { // Only verify if we have a token but no user details
        try {
          const response = await api.get('/api/v1/admin/me');
          // If successful, we can store the user details in the store
          useAdminAuthStore.setState({ user: response.data });
        } catch (error) {
          // The 401 interceptor will handle the logout
          console.error("Token verification failed.", error);
        }
      }
    };

    verifyToken();
  }, [location, token, user]); // Rerun on route change

  return null; // This component does not render anything
};

export default AuthVerify;
