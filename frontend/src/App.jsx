import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ScannerPage from './pages/ScannerPage';
import PlayerPage from './pages/PlayerPage';
import RecoverPinPage from './pages/RecoverPinPage';
import AdminLoginPage from './pages/admin/AdminLoginPage';
import AdminLayout from './components/admin/AdminLayout';
import ProtectedRoute from './components/admin/ProtectedRoute';
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import UsersPage from './pages/admin/UsersPage';
import TitlesPage from './pages/admin/TitlesPage';
import ProductsPage from './pages/admin/ProductsPage';
import BatchesPage from './pages/admin/BatchesPage';
import QRDetailPage from './pages/admin/QRDetailPage';
import LegalPage from './pages/LegalPage';

function App() {
  return (
    <Router>
      <AuthVerify />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/scan" element={<ScannerPage />} />
        <Route path="/play/:qr" element={<PlayerPage />} />
        <Route path="/recover" element={<RecoverPinPage />} />
        <Route path="/legal" element={<LegalPage />} />

        {/* Admin Routes */}
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="titles" element={<TitlesPage />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="batches" element={<BatchesPage />} />
          <Route path="qrcodes/:qr" element={<QRDetailPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
