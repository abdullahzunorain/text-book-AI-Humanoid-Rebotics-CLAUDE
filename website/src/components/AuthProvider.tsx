import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';

interface User {
  user_id: number;
  email: string;
  has_background?: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  hasBackground: boolean;
  loading: boolean;
  signup: (email: string, password: string) => Promise<User>;
  signin: (email: string, password: string) => Promise<User>;
  signout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

const API_URL =
  (typeof window !== 'undefined' &&
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (window as any).__DOCUSAURUS_CUSTOM_FIELDS?.apiUrl) ||
  'http://localhost:8000';

export function AuthProvider({children}: {children: ReactNode}): React.JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const signup = useCallback(
    async (email: string, password: string): Promise<User> => {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({email, password}),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Signup failed');
      }
      const data = await response.json();
      setUser(data);
      return data;
    },
    [],
  );

  const signin = useCallback(
    async (email: string, password: string): Promise<User> => {
      const response = await fetch(`${API_URL}/api/auth/signin`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({email, password}),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Sign in failed');
      }
      const data = await response.json();
      setUser(data);
      return data;
    },
    [],
  );

  const signout = useCallback(async () => {
    await fetch(`${API_URL}/api/auth/signout`, {
      method: 'POST',
      credentials: 'include',
    });
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        hasBackground: user?.has_background ?? false,
        loading,
        signup,
        signin,
        signout,
        checkAuth,
      }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
