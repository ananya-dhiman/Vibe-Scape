import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';
import styles from '../LoginComponent.module.css';

const LoginComponent: React.FC = () => {
  const { user, loading, signInWithGoogle, signInWithEmail, signUpWithEmail} = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [authError, setAuthError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleGoogleSignIn = async () => {
    setAuthError('');
    const result = await signInWithGoogle();
    if (!result.success) setAuthError(result.error || 'Authentication failed');
  };

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    const result = isSignUp
      ? await signUpWithEmail(email, password)
      : await signInWithEmail(email, password);
    if (!result.success) setAuthError(result.error || 'Authentication failed');
  };

  if (loading) return <div className={styles.container}>Loading...</div>;
  if (user) return null;

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <button className={styles.backBtn} onClick={() => navigate(-1)} aria-label="Back">
          &#8592;
        </button>
        <div className={styles.title}>{isSignUp ? 'Sign up' : 'Sign in'}</div>
        {authError && (
          <div style={{ color: '#b91c1c', background: '#fee2e2', borderRadius: 8, padding: 8, marginBottom: 12 }}>
            {authError}
          </div>
        )}
        <form onSubmit={handleEmailSignIn}>
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>Email</label>
            <input
              type="email"
              id="email"
              className={styles.input}
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.label}>Password</label>
            <div className={styles.inputWrap}>
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                className={styles.input}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete={isSignUp ? 'new-password' : 'current-password'}
              />
              <button
                type="button"
                className={styles.eyeBtn}
                onClick={() => setShowPassword(v => !v)}
                tabIndex={-1}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>
          <button type="submit" className={styles.submitBtn}>
            {isSignUp ? 'Create my account' : 'Sign In'}
          </button>
        </form>
        <div className={styles.divider}>
          <div className={styles.dividerLine}></div>
          <span className={styles.dividerText}>or continue with</span>
          <div className={styles.dividerLine}></div>
        </div>
        <button onClick={handleGoogleSignIn} className={styles.googleBtn}>
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" style={{ width: 28, height: 28 }} />
          Google
        </button>
        <div className={styles.switchText}>
          {isSignUp ? (
            <>
              Already have an account?
              <button className={styles.switchBtn} onClick={() => setIsSignUp(false)} type="button">
                Sign in
              </button>
            </>
          ) : (
            <>
              Don't have an account?
              <button className={styles.switchBtn} onClick={() => setIsSignUp(true)} type="button">
                Sign Up
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoginComponent; 