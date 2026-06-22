import { createFileRoute } from "@tanstack/react-router";
import { Mail, Phone, MapPin, Send } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — NEUROX" },
      { name: "description", content: "Get in touch with the NEUROX team for demos, pilots, and partnerships." },
    ],
  }),
  component: Contact,
});

function Contact() {
  const [sent, setSent] = useState(false);
  return (
    <>
      <section className="pt-40 pb-16 bg-ink text-ink-foreground">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Contact</span>
          <h1 className="mt-3 text-5xl md:text-7xl font-bold">Let's build it together.</h1>
          <p className="mt-6 text-lg text-ink-foreground/70 max-w-2xl">
            Whether you're a municipality, an institution, or a fellow student — we'd love to hear from you.
          </p>
        </div>
      </section>

      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6 grid gap-12 lg:grid-cols-[1fr_1.5fr]">
          <div className="space-y-6">
            {[
              { Icon: Mail, t: "Email", v: "vikramchoure607@gmail.com" },
              { Icon: Phone, t: "Phone", v: "+91 8305610712" },
              { Icon: MapPin, t: "Location", v: "India · Bhopal" },
            ].map(({ Icon, t, v }) => (
              <div key={t} className="flex gap-4 items-start">
                <div className="size-12 rounded-xl bg-primary/15 text-primary grid place-items-center shrink-0">
                  <Icon size={20} />
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider">{t}</div>
                  <div className="text-lg font-semibold mt-1">{v}</div>
                </div>
              </div>
            ))}
          </div>

          <form
            onSubmit={(e) => { e.preventDefault(); setSent(true); }}
            className="bg-card rounded-2xl border border-border p-8 space-y-5 shadow-sm"
          >
            <div className="grid sm:grid-cols-2 gap-5">
              <Field label="Full name" name="name" required />
              <Field label="Email" name="email" type="email" required />
            </div>
            <Field label="Organization" name="org" />
            <div>
              <label className="text-sm font-medium">Message</label>
              <textarea
                required
                rows={5}
                className="mt-2 w-full rounded-lg border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Tell us about your project or pilot…"
              />
            </div>
            <button
              type="submit"
              className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-6 py-3 font-medium hover:opacity-90 transition"
            >
              <Send size={16} /> Send message
            </button>
            {sent && (
              <p className="text-sm text-primary font-medium">
                ✓ Thanks! We'll get back to you within 24 hours.
              </p>
            )}
          </form>
        </div>
      </section>
    </>
  );
}

function Field({ label, name, type = "text", required }: { label: string; name: string; type?: string; required?: boolean }) {
  return (
    <div>
      <label className="text-sm font-medium" htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        type={type}
        required={required}
        className="mt-2 w-full rounded-lg border border-border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>
  );
}
