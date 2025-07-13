// Export Firebase configuration
export { default as firebaseApp } from './firebase';
export { auth, googleProvider } from './firebase';

// Export Auth Service
export { default as authService } from './authService';

// Export Auth Context
export { AuthProvider, useAuth } from './AuthContext'; 