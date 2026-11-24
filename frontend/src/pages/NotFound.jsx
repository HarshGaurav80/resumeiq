import { Link } from "react-router-dom";
import { buttonVariants } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
      <p className="text-gradient text-6xl font-extrabold">404</p>
      <h1 className="mt-4 text-xl font-semibold">Page not found</h1>
      <p className="mt-2 text-muted-foreground">The page you are looking for doesn't exist.</p>
      <Link to="/" className={buttonVariants({ variant: "gradient", className: "mt-6" })}>Back to home</Link>
    </div>
  );
}
