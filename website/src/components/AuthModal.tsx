import React, {useState, useCallback} from 'react';
import {useAuth} from './AuthProvider';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSignupSuccess: () => void;
}

type Tab = 'signin' | 'signup';

export default function AuthModal({
  isOpen,
  onClose,
  onSignupSuccess,
}: AuthModalProps): React.JSX.Element | null {
  const [tab, setTab] = useState<Tab>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const {signup, signin} = useAuth();

  const resetForm = useCallback(() => {
    setEmail('');
    setPassword('');
    setError(null);
  }, []);

  const handleTabChange = useCallback(
    (newTab: Tab) => {
      setTab(newTab);
      resetForm();
    },
    [resetForm],
  );

  const validate = (): string | null => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Please enter a valid email address';
    }
    if (tab === 'signup' && password.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!password) {
      return 'Password is required';
    }
    return null;
  };

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const validationError = validate();
      if (validationError) {
        setError(validationError);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        if (tab === 'signup') {
          await signup(email, password);
          onSignupSuccess();
        } else {
          await signin(email, password);
          onClose();
        }
        resetForm();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    },
    [email, password, tab, signup, signin, onClose, onSignupSuccess, resetForm],
  );

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button
          className="auth-modal-close"
          onClick={onClose}
          type="button"
          aria-label="Close">
          &times;
        </button>

        <div className="auth-modal-tabs">
          <button
            className={`auth-tab ${tab === 'signin' ? 'active' : ''}`}
            onClick={() => handleTabChange('signin')}
            type="button">
            Sign In
          </button>
          <button
            className={`auth-tab ${tab === 'signup' ? 'active' : ''}`}
            onClick={() => handleTabChange('signup')}
            type="button">
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="auth-email">Email</label>
            <input
              id="auth-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="auth-password">Password</label>
            <input
              id="auth-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={tab === 'signup' ? 'Min 8 characters' : 'Your password'}
              autoComplete={
                tab === 'signup' ? 'new-password' : 'current-password'
              }
              required
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button
            type="submit"
            className="button button--primary"
            disabled={loading}
            style={{width: '100%'}}>
            {loading
              ? '...'
              : tab === 'signup'
                ? 'Create Account'
                : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
