// Sticky top navigation with mobile menu and dark-mode toggle.
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Link, NavLink } from "react-router-dom";
import { Menu, Moon, Sun, X } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTheme } from "./ThemeProvider.jsx";
import Logo from "./Logo.jsx";

const links = [
  { to: "/", label: "Home", end: true },
  { to: "/analyze", label: "Analyze" },
  { to: "/history", label: "History" },
  { to: "/about", label: "About" },
];

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    cn(
      "rounded-md px-3 py-2 text-sm font-medium transition-colors hover:text-foreground",
      isActive ? "text-foreground bg-muted" : "text-muted-foreground",
    );

  return (
    <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur-lg">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" aria-label="ResumeIQ home" onClick={() => setOpen(false)}>
          <Logo />
        </Link>

        {/* Desktop links */}
        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}>
              {l.label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle dark mode">
            {theme === "dark" ? <Sun /> : <Moon />}
          </Button>
          <Link to="/analyze" className={cn(buttonVariants({ variant: "gradient", size: "sm" }), "hidden sm:inline-flex")}>
            Analyze Resume
          </Link>
          <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setOpen((o) => !o)} aria-label="Open menu">
            {open ? <X /> : <Menu />}
          </Button>
        </div>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t md:hidden"
          >
            <div className="flex flex-col gap-1 px-4 py-3">
              {links.map((l) => (
                <NavLink key={l.to} to={l.to} end={l.end} className={linkClass} onClick={() => setOpen(false)}>
                  {l.label}
                </NavLink>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
