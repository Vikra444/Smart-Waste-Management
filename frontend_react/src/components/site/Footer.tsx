import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer className="bg-ink text-ink-foreground">
      <div className="mx-auto max-w-7xl px-6 py-16 grid gap-12 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="size-9 rounded-md bg-primary grid place-items-center font-display font-bold text-primary-foreground">
              NX
            </div>
            <span className="font-display font-bold text-lg">NEUROX</span>
          </div>
          <p className="text-sm text-ink-foreground/70 max-w-xs">
            AI-powered smart waste management for cleaner, smarter cities.
          </p>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-4 text-primary">Product</h4>
          <ul className="space-y-2 text-sm text-ink-foreground/70">
            <li><Link to="/solutions">Smart Bins</Link></li>
            <li><Link to="/solutions">AI Analytics</Link></li>
            <li><Link to="/solutions">Route Optimization</Link></li>
            <li><Link to="/solutions">Dashboard</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-4 text-primary">Company</h4>
          <ul className="space-y-2 text-sm text-ink-foreground/70">
            <li><Link to="/about">About</Link></li>
            <li><Link to="/use-cases">Use Cases</Link></li>
            <li><Link to="/contact">Contact</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-4 text-primary">Get in touch</h4>
          <p className="text-sm text-ink-foreground/70">hello@neurox.ai</p>
          <p className="text-sm text-ink-foreground/70 mt-1">+91 98765 43210</p>
        </div>
      </div>
      <div className="border-t border-white/10">
        <div className="mx-auto max-w-7xl px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-ink-foreground/50">
          <p>© {new Date().getFullYear()} NEUROX. AI-Based Smart Waste Management System.</p>
          <p>Built with care for sustainable cities.</p>
        </div>
      </div>
    </footer>
  );
}
