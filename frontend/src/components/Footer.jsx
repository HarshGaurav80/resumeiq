// Site footer.
import { Link } from "react-router-dom";
import Logo from "./Logo.jsx";

export default function Footer() {
  return (
    <footer className="mt-16 border-t">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6">
        <div className="flex flex-col items-center gap-1 sm:items-start">
          <Logo />
          <p className="text-xs text-muted-foreground">AI-powered resume analysis · Final-year project</p>
        </div>
        <nav className="flex gap-5 text-sm text-muted-foreground">
          <Link to="/analyze" className="hover:text-foreground">Analyze</Link>
          <Link to="/history" className="hover:text-foreground">History</Link>
          <Link to="/about" className="hover:text-foreground">About</Link>
        </nav>
        <p className="text-xs text-muted-foreground">© {new Date().getFullYear()} ResumeIQ</p>
      </div>
    </footer>
  );
}
