import { Link } from "@tanstack/react-router";
import { Menu, X } from "lucide-react";
import { useState } from "react";

const nav = [
  { to: "/", label: "Home" },
  { to: "/solutions", label: "Solutions" },
  { to: "/architecture", label: "Architecture" },
  { to: "/use-cases", label: "Use Cases" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
] as const;

export function Header() {
  const [open, setOpen] = useState(false);
  return (
    <header className="absolute top-0 left-0 right-0 z-50">
      <div className="mx-auto max-w-7xl px-6 py-5 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="size-9 rounded-md bg-primary grid place-items-center font-display font-bold text-primary-foreground">
            NX
          </div>
          <span className="font-display font-bold text-lg text-ink-foreground tracking-tight">
            NEUROX
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className="text-sm text-ink-foreground/80 hover:text-primary transition-colors"
              activeProps={{ className: "text-primary font-medium" }}
              activeOptions={{ exact: n.to === "/" }}
            >
              {n.label}
            </Link>
          ))}
        </nav>

        <Link
          to="/dashboard"
          className="hidden md:inline-flex items-center rounded-full bg-background text-foreground px-5 py-2.5 text-sm font-medium hover:bg-primary hover:text-primary-foreground transition-colors"
        >
          Launch Console →
        </Link>

        <button
          onClick={() => setOpen(!open)}
          className="md:hidden text-ink-foreground p-2"
          aria-label="Toggle menu"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden bg-ink text-ink-foreground border-t border-white/10">
          <div className="px-6 py-4 flex flex-col gap-3">
            {nav.map((n) => (
              <Link
                key={n.to}
                to={n.to}
                onClick={() => setOpen(false)}
                className="py-2 text-base"
              >
                {n.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
