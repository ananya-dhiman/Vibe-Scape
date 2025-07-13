import React from 'react';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';
import LoginComponent from '../components/LoginComponent'; // or '../auth/LoginComponent' if that's the path
import '../Login.css';

const Login: React.FC = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  // If user is already logged in, redirect to dashboard
  React.useEffect(() => {
    if (user && !loading) {
      navigate('/dashboard');
    }
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="login-bg">
        <div>Loading...</div>
      </div>
    );
  }

  if (user) {
    return null; // Will redirect to dashboard
  }

  return (
    <div className="login-bg">
      <div className="login-card">
        <div className="login-title">Sign in</div>
        <div className="login-desc">
          Discover amazing places and create your perfect vibe
        </div>
        <LoginComponent />
      </div>
    </div>
  );
};

export default Login;