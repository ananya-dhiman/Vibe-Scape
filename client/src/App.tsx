import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Bot from './pages/Bot';
import Login from './pages/Login';
import Place from './pages/Place';
import WishList from './pages/WishList';
import FeedBack from './pages/FeedBack';

const App: React.FC = () => (
  <AuthProvider>
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/bot" 
          element={
            <ProtectedRoute>
              <Bot />
            </ProtectedRoute>
          } 
        />
       
        <Route
          path="/place/:place_id"
          element={
            <ProtectedRoute>
              <Place />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/wishlist"
          element={
            <ProtectedRoute>
              <WishList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/feedback/:place_id"
          element={
            <ProtectedRoute>
              <FeedBack />
            </ProtectedRoute>
          }
        />
        
        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default App;