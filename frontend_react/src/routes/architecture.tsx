import { createFileRoute } from "@tanstack/react-router";
import {
  Cpu, Radio, Brain, Server, MonitorSmartphone, Smartphone,
  CheckCircle2, FileCode, Layers, Presentation, Wrench, Rocket,
} from "lucide-react";
import dashboard from "@/assets/dashboard.jpg";

export const Route = createFileRoute("/architecture")({
  head: () => ({
    meta: [
      { title: "Architecture & Deliverables — NEUROX" },
      { name: "description", content: "System architecture, MVP scope, and event deliverables for the NEUROX smart waste management project." },
    ],
  }),
  component: Architecture,
});

const layers = [
  { Icon: Cpu, tag: "Layer 01", t: "Smart Bin Hardware", d: "Ultrasonic + weight sensors for fill detection, camera module for waste-type imaging, ESP32 microcontroller for on-device processing.", chips: ["ESP32", "HC-SR04", "Load Cell", "OV2640 Cam"] },
  { Icon: Radio, tag: "Layer 02", t: "Data & Communication", d: "Wireless transmission of bin data over LoRa / GSM / Wi-Fi to cloud ingestion APIs with retries and offline buffering.", chips: ["LoRaWAN", "GSM/4G", "MQTT", "REST"] },
  { Icon: Brain, tag: "Layer 03", t: "AI & Analytics Engine", d: "Computer-vision classification (biodegradable / recyclable / hazardous), predictive fill forecasting, and route optimization algorithms.", chips: ["TensorFlow", "OpenCV", "Genetic Algo", "Forecasting"] },
  { Icon: Server, tag: "Layer 04", t: "Backend Services", d: "REST/GraphQL APIs for ingestion & processing, integration hooks for municipal systems, RBAC, audit logs, and encrypted transport.", chips: ["FastAPI", "PostgreSQL", "Redis", "JWT / RBAC"] },
  { Icon: MonitorSmartphone, tag: "Layer 05", t: "Admin Dashboard", d: "Live map of bins, fleet routing UI, alerts queue, KPI charts, and exportable reports for waste management authorities.", chips: ["React", "TanStack", "Mapbox", "Recharts"] },
  { Icon: Smartphone, tag: "Layer 06", t: "Citizen App (Optional)", d: "Report illegal dumping, scan-to-segregate guidance, and incentive points for proper recycling behavior.", chips: ["PWA", "QR Scan", "Rewards"] },
];

const deliverables = [
  { Icon: Rocket, t: "Functional Prototype / MVP", d: "End-to-end working flow: bin → cloud → dashboard with simulated and live sensor data." },
  { Icon: Layers, t: "System Architecture & Design", d: "Block diagrams, data flow, deployment topology, and security model documentation." },
  { Icon: Presentation, t: "Demo Use Case", d: "Live monitoring scenario with optimized collection route generated from live fill levels." },
  { Icon: Brain, t: "AI Model Demonstration", d: "Waste classification demo + predictive analytics for waste-generation trends." },
  { Icon: FileCode, t: "Innovation & Scalability Plan", d: "Roadmap from pilot (10 bins) to city-wide deployment (10,000+ bins) with cost model." },
  { Icon: Presentation, t: "Presentation (PPT)", d: "Problem, approach, architecture, demo, business impact, and future roadmap." },
  { Icon: Wrench, t: "IoT Smart Bin Prototype (Optional)", d: "Physical demo unit with ESP32 + ultrasonic + camera streaming to the dashboard." },
];

const objectives = [
  "Real-time monitoring of waste levels in bins using sensors",
  "Detection & classification of waste types (biodegradable, recyclable, hazardous)",
  "Intelligent route optimization for waste collection vehicles",
  "Alerts and notifications for bin overflow or irregularities",
  "Accurate and timely data collection from distributed bins",
  "Scalable architecture for city-wide deployment",
  "Secure and reliable data transmission",
  "User-friendly interfaces for monitoring and control",
];

function Architecture() {
  return (
    <>
      <section className="relative pt-40 pb-24 bg-ink text-ink-foreground overflow-hidden">
        <img src={dashboard} alt="" className="absolute inset-0 size-full object-cover opacity-25" />
        <div className="absolute inset-0 bg-gradient-to-b from-ink/80 to-ink" />
        <div className="relative mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Architecture & Deliverables</span>
          <h1 className="mt-3 text-5xl md:text-7xl font-bold max-w-4xl">
            A six-layer system, built for real cities.
          </h1>
          <p className="mt-6 text-lg text-ink-foreground/70 max-w-2xl">
            From low-cost sensor hardware to cloud-hosted AI and a citizen-facing app —
            NEUROX covers every layer required by the problem statement.
          </p>
        </div>
      </section>

      {/* OBJECTIVES */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Core Objectives</span>
          <h2 className="mt-3 text-4xl md:text-5xl font-bold max-w-3xl">
            What the system must do.
          </h2>
          <div className="mt-12 grid gap-4 md:grid-cols-2">
            {objectives.map((o) => (
              <div key={o} className="flex gap-3 items-start rounded-xl border border-border bg-card p-5">
                <CheckCircle2 className="text-primary shrink-0 mt-0.5" size={20} />
                <span className="text-foreground/90">{o}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* LAYERS */}
      <section className="py-24 bg-secondary">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">System Architecture</span>
          <h2 className="mt-3 text-4xl md:text-5xl font-bold">Six integrated layers</h2>
          <p className="mt-4 text-muted-foreground text-lg max-w-2xl">
            Each layer is independently deployable and horizontally scalable.
          </p>

          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {layers.map(({ Icon, tag, t, d, chips }) => (
              <div key={t} className="rounded-2xl border border-border bg-card p-7 hover:border-primary/50 hover:shadow-lg transition">
                <div className="flex items-center justify-between">
                  <div className="size-12 rounded-xl bg-primary/15 text-primary grid place-items-center">
                    <Icon size={22} />
                  </div>
                  <span className="text-xs font-semibold text-primary tracking-wider">{tag}</span>
                </div>
                <h3 className="mt-5 text-xl font-semibold">{t}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{d}</p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {chips.map((c) => (
                    <span key={c} className="rounded-full bg-background border border-border px-3 py-1 text-xs font-medium">{c}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DATA FLOW DIAGRAM */}
      <section className="py-24 bg-ink text-ink-foreground">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Data Flow</span>
          <h2 className="mt-3 text-4xl md:text-5xl font-bold">From bin to decision in seconds.</h2>

          <div className="mt-14 grid gap-4 md:grid-cols-5">
            {[
              { n: "01", t: "Sense", d: "Ultrasonic + camera capture" },
              { n: "02", t: "Transmit", d: "LoRa / GSM payload" },
              { n: "03", t: "Ingest", d: "Cloud API + queue" },
              { n: "04", t: "Analyze", d: "AI classify + forecast" },
              { n: "05", t: "Act", d: "Routes + alerts" },
            ].map((s) => (
              <div key={s.n} className="rounded-2xl border border-white/10 p-6 bg-white/5">
                <div className="text-primary text-xs font-semibold tracking-wider">STAGE {s.n}</div>
                <div className="mt-2 text-xl font-display font-bold">{s.t}</div>
                <div className="mt-2 text-sm text-ink-foreground/60">{s.d}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DELIVERABLES */}
      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Event Deliverables</span>
          <h2 className="mt-3 text-4xl md:text-5xl font-bold max-w-3xl">
            Everything we'll present.
          </h2>
          <p className="mt-4 text-muted-foreground text-lg max-w-2xl">
            Mapped 1:1 to the expected deliverables from the problem statement.
          </p>

          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {deliverables.map(({ Icon, t, d }, i) => (
              <div key={t} className="rounded-2xl border border-border bg-card p-7">
                <div className="flex items-center gap-3">
                  <div className="size-10 rounded-lg bg-primary/15 text-primary grid place-items-center">
                    <Icon size={18} />
                  </div>
                  <span className="text-xs font-semibold text-primary">DELIVERABLE {String(i + 1).padStart(2, "0")}</span>
                </div>
                <h3 className="mt-5 text-lg font-semibold">{t}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
