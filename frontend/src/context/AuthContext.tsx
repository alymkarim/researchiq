import { createContext, useContext, useEffect, useState } from "react";

interface AuthState {
  token: string;
  username: string;
}

interface AuthContextType {
  user: AuthState | null;
  login: (token: string, username: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthState | null>(() => {
    const stored = localStorage.getItem("researchiq-auth");
    if (stored) {
      try {
        return JSON.parse(stored) as AuthState;
      } catch {
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem("researchiq-auth", JSON.stringify(user));
    } else {
      localStorage.removeItem("researchiq-auth");
    }
  }, [user]);

  function login(token: string, username: string) {
    setUser({ token, username });
  }

  function logout() {
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
