"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { checkSession, login as loginRequest, logout as logoutRequest } from "@/lib/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (code: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setAuthenticated] = useState(false);
  const [isLoading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    setLoading(true);
    checkSession()
      .then(setAuthenticated)
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (code: string) => {
    await loginRequest(code);
    setAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    await logoutRequest();
    setAuthenticated(false);
  }, []);

  useEffect(() => {
    // Check once, the first time the app loads — every page reads from
    // this shared context instead of hitting GET /session itself.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refresh();
  }, [refresh]);

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
