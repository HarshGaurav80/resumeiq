// Top-level layout and routes.
import { lazy, Suspense, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "sonner";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import { useTheme } from "./components/ThemeProvider.jsx";
import Landing from "./pages/Landing.jsx";
import Analyze from "./pages/Analyze.jsx";
// Heavier pages are code-split and loaded on demand (Recharts only loads with Results)
const Results = lazy(() => import("./pages/Results.jsx"));
const History = lazy(() => import("./pages/History.jsx"));
const About = lazy(() => import("./pages/About.jsx"));
import NotFound from "./pages/NotFound.jsx";

// Fade/slide transition applied to every page
function Page({ children }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="flex-1"
    >
      {children}
    </motion.main>
  );
}

export default function App() {
  const location = useLocation();
  const { theme } = useTheme();

  // Start each new page at the top
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <Suspense fallback={<div className="flex-1" />}>
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<Page><Landing /></Page>} />
            <Route path="/analyze" element={<Page><Analyze /></Page>} />
            <Route path="/results/:id" element={<Page><Results /></Page>} />
            <Route path="/history" element={<Page><History /></Page>} />
            <Route path="/about" element={<Page><About /></Page>} />
            <Route path="*" element={<Page><NotFound /></Page>} />
          </Routes>
        </AnimatePresence>
      </Suspense>
      <Footer />
      <Toaster richColors position="top-right" theme={theme} closeButton />
    </div>
  );
}
