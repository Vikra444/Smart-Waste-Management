import { createFileRoute, Link } from "@tanstack/react-router";
import { Cpu, Eye, Route as RouteIcon, BellRing, BarChart3, Shield, ArrowRight } from "lucide-react";
import smartBin from "@/assets/smart-bin.jpg";

export const Route = createFileRoute("/solutions")({
  head: () => ({
    meta: [
      { title: "Solutions — NEUROX Smart Waste Management" },
      { name: "description", content: "Smart bins, AI waste classification, route optimization and a real-time dashboard for municipal waste authorities." },
    ],
  }),
  component: Solutions,
});

const solutions = [
  { Icon: Cpu, t: "IoT Smart Bins", d: "ESP32-powered bins with ultrasonic fill-level sensors, weight sensors, and onboard cameras. Battery-friendly, weather-sealed.", bullets: ["Ultrasonic + weight sensing", "Solar / Li-ion power", "LoRa, GSM, or Wi-Fi"] },
  { Icon: Eye, t: "AI Waste Classification", d: "Computer-vision models classify waste into biodegradable, recyclable, and hazardous streams in real-time.", bullets: ["CNN-based image recognition", "Edge + cloud inference", "Continuous model retraining"] },
  { Icon: RouteIcon, t: "Route Optimization", d: "Genetic & graph algorithms generate the shortest pickup routes based on live fill levels, fuel cost, and traffic.", bullets: ["Live data-driven", "Multi-vehicle support", "Up to 60% fewer trips"] },
  { Icon: BellRing, t: "Alerts & Notifications", d: "Instant SMS, email, and dashboard alerts for overflow, fire, tamper, and segregation violations.", bullets: ["Configurable thresholds", "Escalation rules", "Multi-channel delivery"] },
  { Icon: BarChart3, t: "Admin Dashboard", d: "Visualize bin status on a live map, monitor KPIs, plan fleets, and export reports for stakeholders.", bullets: ["Heatmaps & analytics", "Fleet management", "PDF / CSV exports"] },
  { Icon: Shield, t: "Secure & Scalable", d: "Role-based access control, encrypted transport, and a microservice backend ready for city-scale loads.", bullets: ["TLS end-to-end", "RBAC for officials", "Horizontally scalable"] },
];

function Solutions() {
  return (
    <>
      <section className="relative pt-40 pb-24 bg-ink text-ink-foreground overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <img src={smartBin} alt="" className="size-full object-cover" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-ink via-ink/90 to-ink/40" />
        <div className="relative mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Solutions</span>
          <h1 className="mt-3 text-5xl md:text-7xl font-bold max-w-3xl">A complete waste intelligence platform.</h1>
          <p className="mt-6 text-lg text-ink-foreground/70 max-w-2xl">
            Six integrated modules — from sensor hardware to the analytics dashboard —
            covering every step of modern waste operations.
          </p>
        </div>
      </section>

      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {solutions.map(({ Icon, t, d, bullets }) => (
            <div key={t} className="rounded-2xl border border-border p-8 bg-card hover:border-primary/50 hover:shadow-lg transition">
              <div className="size-12 rounded-xl bg-primary/15 text-primary grid place-items-center">
                <Icon size={22} />
              </div>
              <h3 className="mt-5 text-xl font-semibold">{t}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{d}</p>
              <ul className="mt-5 space-y-2">
                {bullets.map((b) => (
                  <li key={b} className="flex gap-2 items-start text-sm">
                    <span className="mt-1.5 size-1.5 rounded-full bg-primary shrink-0" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="py-20 bg-primary text-leaf-foreground">
        <div className="mx-auto max-w-5xl px-6 text-center">
          <h2 className="text-3xl md:text-5xl font-bold">Want to see it in action?</h2>
          <Link to="/contact" className="mt-8 inline-flex items-center gap-2 rounded-full bg-ink text-ink-foreground px-7 py-3.5 font-medium">
            Request a demo <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </>
  );
}
