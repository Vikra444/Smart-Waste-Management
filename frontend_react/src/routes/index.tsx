import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity, Recycle, Route as RouteIcon, Bell,
  TrendingUp, Shield, ArrowRight, Cpu, Cloud, BarChart3
} from "lucide-react";
import heroCity from "@/assets/hero-city.jpg";
import smartBin from "@/assets/smart-bin.jpg";
import routeTruck from "@/assets/route-truck.jpg";
import dashboard from "@/assets/dashboard.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "NEUROX — AI Smart Waste Management System" },
      { name: "description", content: "End-to-end AI + IoT waste management. Smart bins, real-time monitoring, route optimization for cleaner urban environments." },
    ],
  }),
  component: Home,
});

function Home() {
  return (
    <>
      {/* HERO */}
      <section className="relative min-h-[100svh] flex items-center text-ink-foreground overflow-hidden">
        <img
          src={heroCity}
          alt="Aerial view of a green smart city"
          width={1920}
          height={1280}
          className="absolute inset-0 size-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-black/30" />
        <div className="relative mx-auto max-w-7xl px-6 pt-32 pb-24 w-full">
          <div className="max-w-3xl">
            <span className="inline-flex items-center gap-2 rounded-full bg-primary/20 backdrop-blur border border-primary/40 px-4 py-1.5 text-xs font-medium text-primary mb-6">
              <span className="size-1.5 rounded-full bg-primary animate-pulse" />
              AI + IoT for Smart Cities
            </span>
            <h1 className="text-5xl md:text-7xl font-bold leading-[1.05]">
              AI-Based Smart<br />Waste Management.
            </h1>
            <p className="mt-6 text-lg md:text-xl text-white/80 max-w-2xl">
              NEUROX integrates IoT-enabled smart bins with AI-driven analytics to monitor
              waste levels, detect waste types, and optimize collection routes — reducing overflow
              and improving urban cleanliness.
            </p>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link to="/contact" className="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-6 py-3 font-medium hover:opacity-90 transition">
                Get in touch <ArrowRight size={18} />
              </Link>
              <Link to="/solutions" className="inline-flex items-center gap-2 rounded-full border border-white/30 px-6 py-3 font-medium hover:bg-white/10 transition">
                Explore solutions
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="bg-primary text-leaf-foreground">
        <div className="mx-auto max-w-7xl px-6 py-20 grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { n: "60%", l: "Reduction in collection trips" },
            { n: "24/7", l: "Real-time bin monitoring" },
            { n: "95%", l: "Waste classification accuracy" },
            { n: "100+", l: "Bins per city node" },
          ].map((s) => (
            <div key={s.l}>
              <div className="text-5xl md:text-6xl font-display font-bold">{s.n}</div>
              <div className="mt-2 text-sm md:text-base text-leaf-foreground/80">{s.l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* PROBLEM */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6 grid gap-12 lg:grid-cols-2 items-center">
          <div>
            <span className="text-xs font-semibold tracking-widest text-primary uppercase">The Challenge</span>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold">
              Cities lose millions to inefficient waste collection.
            </h2>
            <p className="mt-6 text-muted-foreground text-lg">
              Overflowing bins, fixed-schedule pickups, and poor segregation drive up costs
              and harm public health. Municipalities need real-time visibility and data-driven
              decisions to keep streets clean and sustainable.
            </p>
            <ul className="mt-8 space-y-3">
              {[
                "Inefficient collection schedules → overflowing bins",
                "No real-time visibility of bin status",
                "Poor segregation reduces recycling rates",
                "High operational costs & emissions",
              ].map((t) => (
                <li key={t} className="flex gap-3 items-start">
                  <span className="mt-2 size-1.5 rounded-full bg-primary shrink-0" />
                  <span className="text-foreground/80">{t}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="relative">
            <img
              src={smartBin}
              alt="Smart waste bin with sensor"
              width={1280}
              height={960}
              loading="lazy"
              className="rounded-2xl shadow-2xl"
            />
            <div className="absolute -bottom-6 -left-6 bg-ink text-ink-foreground rounded-xl p-5 shadow-xl max-w-xs hidden sm:block">
              <div className="text-xs text-primary font-semibold tracking-wider">FILL LEVEL</div>
              <div className="text-3xl font-display font-bold mt-1">87%</div>
              <div className="text-xs text-ink-foreground/60 mt-1">Bin #A-2041 · MG Road</div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="py-24 bg-secondary">
        <div className="mx-auto max-w-7xl px-6">
          <div className="max-w-2xl">
            <span className="text-xs font-semibold tracking-widest text-primary uppercase">Capabilities</span>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold">Everything a modern city needs</h2>
            <p className="mt-4 text-muted-foreground text-lg">
              Four core modules working together — sensing, intelligence, optimization, action.
            </p>
          </div>

          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              { Icon: Activity, t: "Real-time Monitoring", d: "Ultrasonic & weight sensors report bin fill levels to the cloud every minute." },
              { Icon: Recycle, t: "Waste Classification", d: "Computer vision detects biodegradable, recyclable, and hazardous waste." },
              { Icon: RouteIcon, t: "Route Optimization", d: "AI plans the most efficient collection routes based on live data." },
              { Icon: Bell, t: "Smart Alerts", d: "Instant notifications for overflow, tampering, or fire hazards." },
            ].map(({ Icon, t, d }) => (
              <div key={t} className="bg-card rounded-2xl p-7 border border-border hover:border-primary/50 hover:shadow-lg transition">
                <div className="size-12 rounded-xl bg-primary/15 grid place-items-center text-primary">
                  <Icon size={22} />
                </div>
                <h3 className="mt-5 text-lg font-semibold">{t}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ARCHITECTURE */}
      <section className="py-24 bg-ink text-ink-foreground">
        <div className="mx-auto max-w-7xl px-6 grid gap-12 lg:grid-cols-2 items-center">
          <div>
            <span className="text-xs font-semibold tracking-widest text-primary uppercase">System Architecture</span>
            <h2 className="mt-3 text-4xl md:text-5xl font-bold">
              From sensor to dashboard, end-to-end.
            </h2>
            <p className="mt-6 text-ink-foreground/70 text-lg">
              A scalable pipeline built on IoT microcontrollers, secure wireless transport,
              and cloud-hosted AI models — ready for city-wide deployment.
            </p>

            <div className="mt-10 space-y-5">
              {[
                { Icon: Cpu, t: "Smart Bin Hardware", d: "ESP32 + ultrasonic + camera modules" },
                { Icon: Cloud, t: "Data & Communication", d: "LoRa / GSM / Wi-Fi to cloud APIs" },
                { Icon: BarChart3, t: "AI & Analytics", d: "Vision models + route optimization algorithms" },
                { Icon: Shield, t: "Secure Backend", d: "Role-based access, encrypted transmission" },
              ].map(({ Icon, t, d }, i) => (
                <div key={t} className="flex gap-5 items-start">
                  <div className="size-10 rounded-lg bg-primary/15 text-primary grid place-items-center shrink-0">
                    <Icon size={18} />
                  </div>
                  <div>
                    <div className="text-xs text-primary font-semibold">STAGE 0{i + 1}</div>
                    <div className="font-semibold mt-0.5">{t}</div>
                    <div className="text-sm text-ink-foreground/60">{d}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
            <img
              src={dashboard}
              alt="NEUROX dashboard preview"
              width={1600}
              height={1024}
              loading="lazy"
              className="w-full"
            />
          </div>
        </div>
      </section>

      {/* USE CASE STRIP */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-wrap items-end justify-between gap-6 mb-12">
            <div>
              <span className="text-xs font-semibold tracking-widest text-primary uppercase">Use Cases</span>
              <h2 className="mt-3 text-4xl md:text-5xl font-bold">Built for every scenario</h2>
            </div>
            <Link to="/use-cases" className="inline-flex items-center gap-2 text-primary font-medium">
              See all <ArrowRight size={16} />
            </Link>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              { t: "Municipal Waste", d: "City-wide bin networks with optimized pickup schedules.", img: routeTruck },
              { t: "Smart Campuses", d: "Universities & corporates tracking segregation compliance.", img: heroCity },
              { t: "Recycling Hubs", d: "Vision-based sorting and stream analytics.", img: smartBin },
            ].map((c) => (
              <div key={c.t} className="group rounded-2xl overflow-hidden bg-card border border-border hover:shadow-xl transition">
                <div className="aspect-[4/3] overflow-hidden">
                  <img src={c.img} alt={c.t} loading="lazy" className="size-full object-cover group-hover:scale-105 transition duration-500" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold">{c.t}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{c.d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* IMPACT */}
      <section className="py-24 bg-secondary">
        <div className="mx-auto max-w-5xl px-6 text-center">
          <TrendingUp className="mx-auto text-primary" size={36} />
          <h2 className="mt-6 text-4xl md:text-5xl font-bold">Measurable environmental impact</h2>
          <p className="mt-6 text-muted-foreground text-lg">
            Cleaner streets, lower emissions, higher recycling rates. NEUROX gives
            authorities the data they need to plan smarter and act faster.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-ink text-ink-foreground">
        <div className="mx-auto max-w-5xl px-6 text-center">
          <h2 className="text-4xl md:text-6xl font-bold leading-tight">
            Ready to digitalize<br />your city's waste?
          </h2>
          <p className="mt-6 text-ink-foreground/70 text-lg max-w-2xl mx-auto">
            Let's talk about how NEUROX can power your smart-city initiative.
          </p>
          <Link to="/contact" className="mt-10 inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground px-8 py-4 font-medium hover:opacity-90 transition">
            Contact us <ArrowRight size={18} />
          </Link>
        </div>
      </section>
    </>
  );
}
