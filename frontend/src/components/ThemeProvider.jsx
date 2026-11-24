// Light/dark theme state, persisted in localStorage and applied as a class on <html>.
import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext({ theme: "light", toggleTheme: () => {} });
const STORAGE_KEY = "resumeiq-theme";

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() =>
    document.documentElement.classList.contains("dark") ? "dark" : "light",
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));
  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
