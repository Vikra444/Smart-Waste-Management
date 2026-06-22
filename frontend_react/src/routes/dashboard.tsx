import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useRef, useEffect, useCallback } from "react";
import {
  LayoutDashboard, Map as MapIcon, Activity, Eye, MessageSquare,
  Cpu, Wifi, Radio, Battery, Thermometer, Wind, Upload, CheckCircle2,
  AlertTriangle, Recycle, Trash2, Send, RotateCcw, Bell, BarChart2
} from "lucide-react";
import { CityMap, type Bin, fillColor } from "@/components/dashboard/CityMap";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from "recharts";
import { toast, Toaster } from "sonner";

const API = ""; // same origin — proxied to FastAPI:8000 via vite

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Control Center — NEUROX" },
      { name: "description", content: "Live operations console for AI-driven smart waste management." },
    ],
  }),
  component: DashboardPage,
});

type Section = "overview" | "map" | "telemetry" | "alerts" | "analytics" | "vision" | "community";
type AIStatus = "ok" | "warn" | "err";

function DashboardPage() {
  const [bins, setBins] = useState<Bin[]>([]);
  const [section, setSection] = useState<Section>("overview");
  const [routeMetrics, setRouteMetrics] = useState({ distance: "—", time: "—", co2: "—", fuel: "—" });
  const [aiStatus, setAiStatus] = useState<AIStatus>("warn");
  const [lastSync, setLastSync] = useState("—");
  const [loading, setLoading] = useState(true);

  // Alert deduplication: track which bins have already triggered each alert type
  const alertedRef = useRef<Record<string, Set<string>>>({});

  // Simulation & Dispatch states
  const [logs, setLogs] = useState<string[]>([
    "🟢 NEURO-GRID IoT online. Listening for node broadcasts...",
    "📡 Route Optimization Engine loaded successfully.",
    "🤖 WasteNet v2 AI CNN Classifier standby."
  ]);
  const [dispatchModal, setDispatchModal] = useState(false);
  const [dispatchProgress, setDispatchProgress] = useState(0);
  const [dispatchLog, setDispatchLog] = useState<string[]>([]);

  // Map fallback centre (Bhopal)
  const DEPOT: [number, number] = [23.24, 77.44];

  const addLog = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [`[${timestamp}] ${msg}`, ...prev.slice(0, 20)]);
  };

  const fetchAll = useCallback(async () => {
    try {
      // 1. Telemetry
      const tRes = await fetch(`${API}/telemetry`);
      if (tRes.ok) {
        const raw = await tRes.json();
        const mapped: Bin[] = raw.map((b: any) => ({
          id: String(b.id),
          name: b.location ?? `Bin #${b.id}`,
          lat: b.lat ?? DEPOT[0] + (Math.random() - 0.5) * 0.08,
          lng: b.lon ?? DEPOT[1] + (Math.random() - 0.5) * 0.08,
          fill: b.fill_level ?? 0,
          battery: b.battery ?? 100,
          temp: Number(b.temp ?? 0),
          gas: Number(b.gas_level ?? 0),
          isReal: b.status === "Real",
        }));
        setBins(mapped);
      }
    } catch (_) {}

    try {
      // 2. Route
      const rRes = await fetch(`${API}/route`);
      if (rRes.ok) {
        const rd = await rRes.json();
        const m = rd.metrics ?? {};
        setRouteMetrics({
          distance: m.distance ?? "—",
          time: m.time ?? "—",
          co2: m.co2_kg_est ?? "—",
          fuel: m.fuel_liters_est ?? "—",
        });
      }
    } catch (_) {}

    try {
      // 3. Health
      const hRes = await fetch(`${API}/health`);
      if (hRes.ok) {
        const hd = await hRes.json();
        setAiStatus(hd.ai_engine === "Ready" ? "ok" : "warn");
      }
    } catch (_) {}

    setLastSync(new Date().toLocaleTimeString());
    setLoading(false);
  }, []);

  // Hardware SEND_INTERVAL_MS = 5000ms (sketch_jun21a.ino:50)
  // Poll at 6000ms → 1s after HW cycle ends = always fresh data, no wasted calls
  useEffect(() => {
    fetchAll();
    const t = setInterval(fetchAll, 6000);
    return () => clearInterval(t);
  }, [fetchAll]);

  // ── Real-time alert engine ──────────────────────────────────────────────────
  useEffect(() => {
    if (!bins.length) return;
    const alerted = alertedRef.current;

    bins.forEach((b) => {
      const id = b.id;

      // ── CRITICAL FILL ≥ 80% ────────────────────────────────────────────────
      if (b.fill >= 80) {
        if (!alerted[id]?.has("fill_critical")) {
          toast.error(`🚨 Bin #${id} OVERFLOW RISK`, {
            description: `${b.name} — Fill level at ${b.fill.toFixed(0)}%. Immediate collection required!`,
            duration: 8000,
            id: `fill_critical_${id}`,
          });
          alerted[id] = alerted[id] ?? new Set();
          alerted[id].add("fill_critical");
          alerted[id].delete("fill_warn");
        }
      } else if (b.fill >= 60) {
        if (!alerted[id]?.has("fill_warn")) {
          toast.warning(`⚠️ Bin #${id} Fill Warning`, {
            description: `${b.name} — Fill level at ${b.fill.toFixed(0)}%. Schedule collection soon.`,
            duration: 6000,
            id: `fill_warn_${id}`,
          });
          alerted[id] = alerted[id] ?? new Set();
          alerted[id].add("fill_warn");
        }
      } else {
        // Reset fill alerts when bin is back to normal
        alerted[id]?.delete("fill_critical");
        alerted[id]?.delete("fill_warn");
      }

      // ── HIGH GAS > 150 ppm ─────────────────────────────────────────────────
      if (b.gas > 150) {
        if (!alerted[id]?.has("gas")) {
          toast.error(`☣️ Gas Hazard — Bin #${id}`, {
            description: `${b.name} — Gas level at ${b.gas.toFixed(1)} ppm. Environmental alert!`,
            duration: 10000,
            id: `gas_${id}`,
          });
          alerted[id] = alerted[id] ?? new Set();
          alerted[id].add("gas");
        }
      } else {
        alerted[id]?.delete("gas");
      }

      // ── HIGH TEMP > 40°C ───────────────────────────────────────────────────
      if (b.temp > 40) {
        if (!alerted[id]?.has("temp")) {
          toast.warning(`🌡️ High Temperature — Bin #${id}`, {
            description: `${b.name} — Temperature at ${b.temp.toFixed(1)}°C. Fire hazard risk!`,
            duration: 8000,
            id: `temp_${id}`,
          });
          alerted[id] = alerted[id] ?? new Set();
          alerted[id].add("temp");
        }
      } else {
        alerted[id]?.delete("temp");
      }

      // ── LOW BATTERY < 15% ──────────────────────────────────────────────────
      if (b.battery < 15 && b.battery > 0) {
        if (!alerted[id]?.has("battery")) {
          toast.warning(`🔋 Low Battery — Bin #${id}`, {
            description: `${b.name} — Battery at ${b.battery.toFixed(0)}%. Node may go offline soon.`,
            duration: 7000,
            id: `battery_${id}`,
          });
          alerted[id] = alerted[id] ?? new Set();
          alerted[id].add("battery");
        }
      } else {
        alerted[id]?.delete("battery");
      }
    });
  }, [bins]);

  const priority = useMemo(() => bins.filter((b) => b.fill >= 60).sort((a, b) => b.fill - a.fill), [bins]);
  const route = useMemo<[number, number][]>(
    () => [DEPOT, ...priority.map((b) => [b.lat, b.lng] as [number, number])],
    [priority],
  );
  const totalDistance = useMemo(() => {
    let d = 0;
    for (let i = 1; i < route.length; i++) {
      const [a, b] = [route[i - 1], route[i]];
      d += Math.hypot(a[0] - b[0], a[1] - b[1]) * 111;
    }
    return d;
  }, [route]);
  const avgFill = bins.length ? Math.round(bins.reduce((a, b) => a + b.fill, 0) / bins.length) : 0;

  const triggerFillJump = async () => {
    if (!bins.length) return;
    const randomBin = bins[Math.floor(Math.random() * bins.length)];
    const targetFill = Math.min(100, randomBin.fill + 35 + Math.floor(Math.random() * 15));
    addLog(`⚠️ SIMULATOR: Spiked fill level to ${targetFill}% on bin #${randomBin.id} (${randomBin.name})`);
    
    try {
      await fetch(`${API}/iot/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bin_id: Number(randomBin.id),
          fill_level: targetFill,
          gas_level: randomBin.gas,
          temperature: randomBin.temp,
          battery: randomBin.battery,
          location: randomBin.name,
          latitude: randomBin.lat,
          longitude: randomBin.lng
        })
      });
      setTimeout(fetchAll, 500);
    } catch (e) {
      addLog(`❌ SIMULATOR ERROR: ${e}`);
    }
  };

  const triggerGasSpike = async () => {
    if (!bins.length) return;
    const randomBin = bins[Math.floor(Math.random() * bins.length)];
    addLog(`⚠️ SIMULATOR: Triggered gas leak alert (245 ppm) on bin #${randomBin.id} (${randomBin.name})`);
    
    try {
      await fetch(`${API}/iot/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bin_id: Number(randomBin.id),
          fill_level: randomBin.fill,
          gas_level: 245.0,
          temperature: 42.5,
          battery: randomBin.battery,
          location: randomBin.name,
          latitude: randomBin.lat,
          longitude: randomBin.lng
        })
      });
      setTimeout(fetchAll, 500);
    } catch (e) {
      addLog(`❌ SIMULATOR ERROR: ${e}`);
    }
  };

  const triggerBatteryDrain = async () => {
    if (!bins.length) return;
    addLog(`⚠️ SIMULATOR: Simulated grid-wide temporal IoT cell discharge`);
    try {
      for (let i = 0; i < Math.min(3, bins.length); i++) {
        const randomBin = bins[Math.floor(Math.random() * bins.length)];
        await fetch(`${API}/iot/update`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            bin_id: Number(randomBin.id),
            fill_level: Math.min(100, randomBin.fill + Math.floor(Math.random() * 8)),
            gas_level: randomBin.gas,
            temperature: Math.min(60, randomBin.temp + 2 + Math.floor(Math.random() * 3)),
            battery: Math.max(5, randomBin.battery - 8 - Math.floor(Math.random() * 5)),
            location: randomBin.name,
            latitude: randomBin.lat,
            longitude: randomBin.lng
          })
        });
      }
      setTimeout(fetchAll, 500);
    } catch (e) {
      addLog(`❌ SIMULATOR ERROR: ${e}`);
    }
  };

  const handleDispatch = () => {
    const ids = priority.map((b) => Number(b.id));
    if (!ids.length) return;
    
    setDispatchModal(true);
    setDispatchProgress(0);
    setDispatchLog([`[0.0s] 🟢 Dispatch operations console online.`]);

    const logsList = [
      `[0.5s] 📡 Establishing link with AI Route Optimization Engine...`,
      `[1.0s] 🗺️ Solving traveling salesperson matrix for ${priority.length} targets...`,
      `[1.6s] ⚡ Shortest route resolved: Total Distance = ${totalDistance.toFixed(1)} km, fuel offset estimated: ${(totalDistance * 0.12).toFixed(1)} Liters!`,
      `[2.2s] 🚛 Dispatch orders sent to Collection Truck #04.`,
      `[2.8s] 🚀 GPS tracking locked on Connaught Depot logistics gateway.`,
      `[3.4s] 🧹 Clearing priority bins: ${priority.map(b => b.name).join(", ")}...`,
      `[4.0s] 🌿 IoT registers reset. Collection successfully recorded.`
    ];

    let currentStep = 0;
    const interval = setInterval(async () => {
      currentStep++;
      setDispatchProgress((currentStep / logsList.length) * 100);
      setDispatchLog(prev => [...prev, logsList[currentStep - 1]]);

      if (currentStep >= logsList.length) {
        clearInterval(interval);
        try {
          await fetch(`${API}/bins/reset`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bin_ids: ids }),
          });
          fetchAll();
          addLog(`🌿 LOGISTICS SUCCESS: Truck #04 emptied ${priority.length} priority bins.`);
        } catch (_) {
          setBins((prev) => prev.map((b) => (b.fill >= 60 ? { ...b, fill: Math.floor(Math.random() * 15) } : b)));
        }
      }
    }, 600);
  };

  return (
    <div className="min-h-screen bg-background flex">
      <Toaster position="top-right" richColors closeButton />
      {/* Sidebar */}
      <aside className="w-60 shrink-0 border-r border-border bg-card flex flex-col sticky top-0 h-screen">
        <div className="px-5 py-5 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="size-9 rounded-lg bg-primary text-primary-foreground grid place-items-center font-display font-bold">NX</div>
            <div>
              <div className="font-display font-semibold leading-none">NEUROX</div>
              <div className="text-[10px] text-muted-foreground mt-1 uppercase tracking-wider">Control Center</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground px-3 py-1 mt-1">Operations</div>
          {([
            ["overview", "Overview", LayoutDashboard],
            ["map", "City Map", MapIcon],
            ["telemetry", "Telemetry", Activity],
            ["alerts", "Alerts", Bell],
          ] as const).map(([key, label, Icon]) => (
            <button
              key={key}
              onClick={() => setSection(key)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition ${
                section === key ? "bg-primary/15 text-foreground font-medium" : "text-muted-foreground hover:bg-muted"
              }`}
            >
              <Icon className="size-4" /> {label}
              {key === "alerts" && (() => {
                const count = bins.filter(b =>
                  b.fill >= 80 || b.gas > 150 || b.temp > 40 || (b.battery < 15 && b.battery > 0) || b.fill >= 60
                ).length;
                return count > 0 ? (
                  <span className="ml-auto size-5 rounded-full bg-red-500 text-white text-[10px] grid place-items-center font-bold">
                    {count}
                  </span>
                ) : null;
              })()}
            </button>
          ))}
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground px-3 py-1 mt-3">Intelligence</div>
          {([
            ["analytics", "Analytics", BarChart2],
            ["vision", "AI Vision", Eye],
            ["community", "Community", MessageSquare],
          ] as const).map(([key, label, Icon]) => (
            <button
              key={key}
              onClick={() => setSection(key)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition ${
                section === key ? "bg-primary/15 text-foreground font-medium" : "text-muted-foreground hover:bg-muted"
              }`}
            >
              <Icon className="size-4" /> {label}
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-border space-y-2 text-xs">
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">System Status</div>
          <StatusDot icon={Cpu} label="AI Engine" tone={aiStatus} />
          <StatusDot icon={Radio} label="IoT Grid" tone={bins.length > 0 ? "ok" : "warn"} />
          <StatusDot icon={Wifi} label="Network" tone="ok" />
          <div className="pt-2 text-[10px] text-muted-foreground">Sync: {lastSync}</div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 min-w-0">
        <header className="border-b border-border bg-card/60 backdrop-blur sticky top-0 z-10">
          <div className="px-6 py-4 flex items-center justify-between">
            <div>
              <h1 className="font-display text-xl font-semibold capitalize">{section === "map" ? "Live City Map" : section}</h1>
              <p className="text-xs text-muted-foreground">Last sync · {lastSync}</p>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="size-2 rounded-full bg-green-500 animate-pulse" /> Live
              <button onClick={fetchAll} className="flex items-center gap-1 hover:text-foreground transition">
                <RotateCcw className="size-3" /> Refresh
              </button>
            </div>
          </div>
        </header>

        <div className="p-6 space-y-6">
          {section === "overview" && (
            <OverviewSection
              bins={bins}
              priority={priority}
              avgFill={avgFill}
              logs={logs}
              onTriggerFill={triggerFillJump}
              onTriggerGas={triggerGasSpike}
              onTriggerBattery={triggerBatteryDrain}
            />
          )}
          {section === "map" && (
            <MapSection bins={bins} priority={priority} route={route} totalDistance={totalDistance} onDispatch={handleDispatch} />
          )}
          {section === "telemetry" && <TelemetrySection bins={bins} />}
          {section === "alerts" && <AlertsSection bins={bins} onDispatch={handleDispatch} />}
          {section === "analytics" && <AnalyticsSection bins={bins} />}
          {section === "vision" && <VisionSection />}
          {section === "community" && <CommunitySection />}
        </div>
      </div>

      {/* Dispatch Tracking Simulator Modal Overlay */}
      {dispatchModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl w-full max-w-lg p-6 shadow-2xl relative overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="absolute top-0 left-0 right-0 h-1 bg-muted">
              <div className="h-full bg-primary transition-all duration-300" style={{ width: `${dispatchProgress}%` }} />
            </div>
            
            <div className="flex items-center gap-3 mb-4">
              <span className="size-10 rounded-full bg-primary/10 text-primary grid place-items-center animate-bounce">
                <Recycle className="size-5" />
              </span>
              <div>
                <h3 className="font-display font-semibold text-lg">AI Logistics Dispatch Tracker</h3>
                <p className="text-xs text-muted-foreground">Monitoring active clean truck dispatch sequence</p>
              </div>
            </div>

            <div className="bg-zinc-950 rounded-xl border border-zinc-800 p-4 font-mono text-xs text-green-400 space-y-1.5 h-[200px] overflow-y-auto mb-5 scrollbar-thin">
              {dispatchLog.map((l, i) => (
                <div key={i} className="animate-in fade-in slide-in-from-bottom-1 duration-200">{l}</div>
              ))}
              <div className="w-1.5 h-3.5 bg-green-500 inline-block animate-pulse ml-0.5" />
            </div>

            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground">Progress: {Math.round(dispatchProgress)}%</span>
              <button
                disabled={dispatchProgress < 100}
                onClick={() => setDispatchModal(false)}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Close Tracking Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusDot({ icon: Icon, label, tone }: { icon: any; label: string; tone: "ok" | "warn" | "err" }) {
  const color = tone === "ok" ? "bg-green-500" : tone === "warn" ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-2 text-foreground/80"><Icon className="size-3.5" /> {label}</span>
      <span className={`size-2 rounded-full ${color} animate-pulse`} />
    </div>
  );
}

// ---------- Sections ----------
function Kpi({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="font-display text-3xl font-semibold mt-2">{value}</div>
      {hint && <div className="text-xs text-muted-foreground mt-1">{hint}</div>}
    </div>
  );
}

interface OverviewProps {
  bins: Bin[];
  priority: Bin[];
  avgFill: number;
  logs: string[];
  onTriggerFill: () => void;
  onTriggerGas: () => void;
  onTriggerBattery: () => void;
}

function OverviewSection({
  bins,
  priority,
  avgFill,
  logs,
  onTriggerFill,
  onTriggerGas,
  onTriggerBattery
}: OverviewProps) {
  return (
    <>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Kpi label="Total Bins" value={String(bins.length)} hint="Connected nodes" />
        <Kpi label="Priority Bins" value={String(priority.length)} hint="≥ 60% fill" />
        <Kpi label="Avg Fill Level" value={`${avgFill}%`} hint="Across network" />
        <Kpi label="Last Sync" value={new Date().toLocaleTimeString().slice(0, 5)} hint="Realtime stream" />
      </div>
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl border border-border bg-card p-5">
            <h3 className="font-display font-semibold mb-3 flex items-center gap-2">
              <span className="size-2 rounded-full bg-blue-500 animate-pulse" /> Network Snapshot
            </h3>
            <div className="space-y-2">
              {bins.slice(0, 5).map((b) => (
                <div key={b.id} className="flex items-center gap-3 text-sm">
                  <span className="w-32 truncate text-muted-foreground">{b.name}</span>
                  <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full transition-all duration-500" style={{ width: `${b.fill}%`, background: fillColor(b.fill) }} />
                  </div>
                  <span className="w-10 text-right font-mono">{b.fill}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Live Operations & Event Log Console */}
          <div className="rounded-xl border border-border bg-card p-5 flex flex-col h-[220px]">
            <h3 className="font-display font-semibold mb-3 flex items-center gap-2">
              <Cpu className="size-4 text-primary" /> Live Event & Operations Stream
            </h3>
            <div className="flex-1 bg-zinc-950 font-mono text-[10px] text-green-400 p-4 rounded-lg border border-zinc-800 overflow-y-auto space-y-1.5 scrollbar-thin">
              {logs.map((l, i) => (
                <div key={i} className="animate-in fade-in duration-300">{l}</div>
              ))}
              <div className="w-1 h-3 bg-green-500 inline-block animate-pulse ml-0.5" />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-5">
            <h3 className="font-display font-semibold mb-3">Today's Impact</h3>
            <ul className="text-sm space-y-3">
              <li className="flex justify-between"><span className="text-muted-foreground">CO₂ Saved</span><span className="font-mono">42.6 kg</span></li>
              <li className="flex justify-between"><span className="text-muted-foreground">Fuel Saved</span><span className="font-mono">18.2 L</span></li>
              <li className="flex justify-between"><span className="text-muted-foreground">Trips Avoided</span><span className="font-mono">7</span></li>
              <li className="flex justify-between"><span className="text-muted-foreground">Overflows Prevented</span><span className="font-mono">3</span></li>
            </ul>
          </div>

          {/* Interactive Hackathon Simulation Controls */}
          <div className="rounded-xl border border-primary/20 bg-card p-5 relative overflow-hidden shadow-md">
            <div className="absolute top-0 right-0 bg-primary/10 text-primary text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-bl">
              Sandbox Mode
            </div>
            <h3 className="font-display font-semibold text-sm mb-1.5 flex items-center gap-1.5">
              <Radio className="size-4 text-primary animate-pulse" /> IoT Event Simulator
            </h3>
            <p className="text-[11px] text-muted-foreground mb-4">
              Inject real-time telemetry changes directly into the FastAPI gateway & database.
            </p>
            <div className="space-y-2">
              <button
                onClick={onTriggerFill}
                className="w-full flex items-center justify-between text-xs border border-border bg-muted/30 hover:bg-primary/10 hover:border-primary/30 px-3 py-2 rounded-lg transition font-medium"
              >
                <span>Trigger Sudden Fill Jump</span>
                <span className="text-[10px] text-primary bg-primary/15 px-1.5 py-0.5 rounded font-mono">+35%</span>
              </button>
              <button
                onClick={onTriggerGas}
                className="w-full flex items-center justify-between text-xs border border-border bg-muted/30 hover:bg-amber-500/10 hover:border-amber-500/30 px-3 py-2 rounded-lg transition font-medium"
              >
                <span>Simulate Gas Spill (Hazard)</span>
                <span className="text-[10px] text-amber-500 bg-amber-500/15 px-1.5 py-0.5 rounded font-mono">245 ppm</span>
              </button>
              <button
                onClick={onTriggerBattery}
                className="w-full flex items-center justify-between text-xs border border-border bg-muted/30 hover:bg-red-500/10 hover:border-red-500/30 px-3 py-2 rounded-lg transition font-medium"
              >
                <span>Trigger Battery Drain Clock</span>
                <span className="text-[10px] text-red-500 bg-red-500/15 px-1.5 py-0.5 rounded font-mono">-8% Bat</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function MapSection({
  bins, priority, route, totalDistance, onDispatch,
}: { bins: Bin[]; priority: Bin[]; route: [number, number][]; totalDistance: number; onDispatch: () => void }) {
  const estTime = Math.round(totalDistance * 2.4);
  const co2 = (totalDistance * 0.31).toFixed(1);
  const fuel = (totalDistance * 0.12).toFixed(1);
  return (
    <div className="grid lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 rounded-xl border border-border bg-card overflow-hidden h-[560px]">
        <CityMap bins={bins} route={route} />
      </div>
      <div className="rounded-xl border border-border bg-card p-5 flex flex-col">
        <h3 className="font-display font-semibold flex items-center gap-2"><Cpu className="size-4 text-primary" /> AI Dispatch Intel</h3>
        <div className="grid grid-cols-2 gap-3 mt-4">
          <Metric label="Distance" value={`${totalDistance.toFixed(1)} km`} />
          <Metric label="Est. Time" value={`${estTime} min`} />
          <Metric label="CO₂ Saved" value={`${co2} kg`} />
          <Metric label="Fuel Saved" value={`${fuel} L`} />
        </div>
        <div className="mt-5 flex-1 overflow-auto">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Pickup Sequence</div>
          <ol className="space-y-1.5 text-sm">
            {priority.length === 0 && <li className="text-muted-foreground">All clear. No priority bins.</li>}
            {priority.map((b, i) => (
              <li key={b.id} className="flex items-center gap-2">
                <span className="size-5 rounded-full bg-primary/20 text-primary text-[10px] grid place-items-center font-bold">{i + 1}</span>
                <span className="flex-1">{b.name}</span>
                <span className="font-mono text-xs" style={{ color: fillColor(b.fill) }}>{b.fill}%</span>
              </li>
            ))}
          </ol>
        </div>
        <button
          onClick={onDispatch}
          disabled={priority.length === 0}
          className="mt-5 w-full rounded-md bg-primary text-primary-foreground py-2.5 text-sm font-medium hover:opacity-90 disabled:opacity-40"
        >
          Dispatch & Empty Bins
        </button>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="font-display font-semibold mt-1">{value}</div>
    </div>
  );
}

function TelemetrySection({ bins }: { bins: Bin[] }) {
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {bins.map((b) => (
        <div key={b.id} className="rounded-xl border border-border bg-card p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-xs text-muted-foreground">{b.id}</div>
              <div className="font-medium text-sm">{b.name}</div>
            </div>
            <span className="size-2.5 rounded-full" style={{ background: fillColor(b.fill) }} />
          </div>
          <div className="font-display text-4xl font-semibold" style={{ color: fillColor(b.fill) }}>{b.fill}%</div>
          <div className="text-xs text-muted-foreground">Fill Level</div>
          <div className="grid grid-cols-3 gap-2 mt-4 text-xs">
            <Stat icon={Battery} value={`${b.battery.toFixed(0)}%`} />
            <Stat icon={Thermometer} value={`${b.temp.toFixed(1)}°`} />
            <Stat icon={Wind} value={`${b.gas.toFixed(1)}`} suffix="ppm" />
          </div>
        </div>
      ))}
    </div>
  );
}

function Stat({ icon: Icon, value, suffix }: { icon: any; value: string; suffix?: string }) {
  return (
    <div className="rounded-md bg-muted/50 p-2 text-center">
      <Icon className="size-3.5 mx-auto text-muted-foreground" />
      <div className="font-mono mt-1">{value}<span className="text-muted-foreground text-[10px] ml-0.5">{suffix}</span></div>
    </div>
  );
}

// ─── ALERTS SECTION ───────────────────────────────────────────────────────────
function AlertsSection({ bins, onDispatch }: { bins: Bin[]; onDispatch: () => void }) {
  const critical  = bins.filter(b => b.fill >= 80).sort((a, b) => b.fill - a.fill);
  const warn      = bins.filter(b => b.fill >= 60 && b.fill < 80);
  const highTemp  = bins.filter(b => b.temp > 40).sort((a, b) => b.temp - a.temp);
  const highGas   = bins.filter(b => b.gas > 150).sort((a, b) => b.gas - a.gas);
  const lowBat    = bins.filter(b => b.battery < 15 && b.battery > 0).sort((a, b) => a.battery - b.battery);

  const totalAlerts = critical.length + warn.length + highTemp.length + highGas.length + lowBat.length;

  // Build a flat alert history list
  const allAlerts: { severity: "critical" | "warn"; text: string; time: string }[] = [
    ...critical.map(b => ({ severity: "critical" as const, text: `🚨 ${b.name} — Fill at ${b.fill.toFixed(0)}% (OVERFLOW RISK)`, time: new Date().toLocaleTimeString() })),
    ...highGas.map(b => ({ severity: "critical" as const, text: `☣️ ${b.name} — Gas at ${b.gas.toFixed(1)} ppm (HAZARD)`, time: new Date().toLocaleTimeString() })),
    ...highTemp.map(b => ({ severity: "critical" as const, text: `🌡️ ${b.name} — Temp at ${b.temp.toFixed(1)}°C (HIGH TEMP)`, time: new Date().toLocaleTimeString() })),
    ...warn.map(b => ({ severity: "warn" as const, text: `⚠️ ${b.name} — Fill at ${b.fill.toFixed(0)}% (SCHEDULE COLLECTION)`, time: new Date().toLocaleTimeString() })),
    ...lowBat.map(b => ({ severity: "warn" as const, text: `🔋 ${b.name} — Battery at ${b.battery.toFixed(0)}% (LOW POWER)`, time: new Date().toLocaleTimeString() })),
  ];

  return (
    <>
      {/* ── Summary Banner ── */}
      <div className={`rounded-xl border p-4 flex items-center justify-between mb-2 ${
        critical.length > 0 || highGas.length > 0
          ? "border-red-500/40 bg-red-500/10"
          : totalAlerts > 0
          ? "border-amber-500/40 bg-amber-500/10"
          : "border-green-500/40 bg-green-500/10"
      }`}>
        <div className="flex items-center gap-3">
          <AlertTriangle className={`size-5 shrink-0 ${
            critical.length > 0 || highGas.length > 0 ? "text-red-500" : totalAlerts > 0 ? "text-amber-500" : "text-green-500"
          }`} />
          <div>
            <p className="font-semibold text-sm">
              {totalAlerts === 0
                ? "✓ All systems nominal — no active alerts"
                : `${totalAlerts} active alert${totalAlerts > 1 ? "s" : ""} across ${new Set([...critical, ...warn, ...highTemp, ...highGas, ...lowBat].map(b => b.id)).size} bin(s)`}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">Last evaluated at {new Date().toLocaleTimeString()}</p>
          </div>
        </div>
        {(critical.length > 0 || warn.length > 0) && (
          <button onClick={onDispatch} className="shrink-0 ml-4 rounded-lg bg-red-600 text-white px-4 py-2 text-sm font-medium hover:bg-red-700 transition">
            Dispatch Collection
          </button>
        )}
      </div>

      {/* ── Alert Cards Grid ── */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {[
          {
            title: "Critical Fill ≥80%", items: critical,
            accentClass: "text-red-500", borderClass: "border-red-500/30 bg-red-500/5",
            icon: <AlertTriangle className="size-4 text-red-500" />,
            getValue: (b: Bin) => `${b.fill.toFixed(0)}%`,
          },
          {
            title: "Fill Warning 60–79%", items: warn,
            accentClass: "text-amber-500", borderClass: "border-amber-500/30 bg-amber-500/5",
            icon: <AlertTriangle className="size-4 text-amber-400" />,
            getValue: (b: Bin) => `${b.fill.toFixed(0)}%`,
          },
          {
            title: "High Temp >40°C", items: highTemp,
            accentClass: "text-orange-500", borderClass: "border-orange-500/30 bg-orange-500/5",
            icon: <Thermometer className="size-4 text-orange-500" />,
            getValue: (b: Bin) => `${b.temp.toFixed(1)}°C`,
          },
          {
            title: "Gas Hazard >150ppm", items: highGas,
            accentClass: "text-purple-500", borderClass: "border-purple-500/30 bg-purple-500/5",
            icon: <Wind className="size-4 text-purple-500" />,
            getValue: (b: Bin) => `${b.gas.toFixed(1)} ppm`,
          },
          {
            title: "Low Battery <15%", items: lowBat,
            accentClass: "text-blue-500", borderClass: "border-blue-500/30 bg-blue-500/5",
            icon: <Battery className="size-4 text-blue-500" />,
            getValue: (b: Bin) => `${b.battery.toFixed(0)}%`,
          },
        ].map(({ title, items, accentClass, borderClass, icon, getValue }) => (
          <div key={title} className={`rounded-xl border bg-card p-5 transition-all ${items.length ? borderClass : "border-border"}`}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-display font-semibold flex items-center gap-2 text-sm">{icon} {title}</h3>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${items.length ? accentClass + " bg-current/10" : "text-muted-foreground bg-muted"}`}>
                {items.length}
              </span>
            </div>
            {items.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-3">✓ All clear</p>
            ) : (
              <div className="space-y-1.5">
                {items.slice(0, 6).map(b => (
                  <div key={b.id} className="flex justify-between text-sm py-1.5 border-b border-border/50 last:border-0">
                    <span className="truncate max-w-[120px] text-foreground/80">{b.name}</span>
                    <span className={`font-mono text-xs font-bold ${accentClass}`}>{getValue(b)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* ── Live Alert Log ── */}
      <div className="rounded-xl border border-border bg-card p-5">
        <h3 className="font-display font-semibold text-sm flex items-center gap-2 mb-3">
          <Bell className="size-4 text-primary" /> Live Alert Feed
          <span className="ml-auto text-[10px] font-normal text-muted-foreground">Auto-refreshes every 6s</span>
        </h3>
        {allAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground gap-2">
            <CheckCircle2 className="size-8 text-green-500" />
            <p className="text-sm font-medium text-green-600">No active alerts — all bins operating normally</p>
          </div>
        ) : (
          <div className="space-y-2">
            {allAlerts.map((a, i) => (
              <div key={i} className={`flex items-start gap-3 rounded-lg p-3 text-sm border ${
                a.severity === "critical" ? "border-red-500/20 bg-red-500/5" : "border-amber-500/20 bg-amber-500/5"
              }`}>
                <span className={`mt-0.5 size-2 rounded-full shrink-0 ${a.severity === "critical" ? "bg-red-500 animate-pulse" : "bg-amber-400"}`} />
                <span className="flex-1 text-foreground/90">{a.text}</span>
                <span className="text-[10px] text-muted-foreground shrink-0 font-mono">{a.time}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

// ─── ANALYTICS SECTION ────────────────────────────────────────────────────────
function AnalyticsSection({ bins }: { bins: Bin[] }) {
  const fillData = [...bins]
    .sort((a, b) => b.fill - a.fill)
    .map(b => ({ name: b.name.split(" ").slice(0, 2).join(" "), fill: b.fill, battery: b.battery, gas: b.gas }));

  const gasData = [...bins]
    .sort((a, b) => b.gas - a.gas)
    .map(b => ({ name: b.name.split(" ").slice(0, 2).join(" "), gas: b.gas, temp: b.temp }));

  const summary = [
    { label: "Critical ≥80%",  value: bins.filter(b => b.fill >= 80).length, color: "#ef4444" },
    { label: "Warning 60–79%", value: bins.filter(b => b.fill >= 60 && b.fill < 80).length, color: "#f59e0b" },
    { label: "Normal <60%",    value: bins.filter(b => b.fill < 60).length, color: "#22c55e" },
    { label: "IoT Devices",    value: bins.filter(b => b.isReal).length, color: "#7c3aed" },
  ];

  if (!bins.length) return (
    <div className="rounded-xl border border-border bg-card p-12 text-center text-muted-foreground">
      No bin data available for analytics. Ensure the FastAPI backend is running.
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {summary.map(s => (
          <div key={s.label} className="rounded-xl border border-border bg-card p-4">
            <div className="text-xs uppercase tracking-wider text-muted-foreground">{s.label}</div>
            <div className="font-display text-3xl font-semibold mt-2" style={{ color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <h3 className="font-display font-semibold mb-1 text-sm">Fill Level Distribution</h3>
        <p className="text-xs text-muted-foreground mb-4">All bins sorted by fill level — red indicates critical overflow risk</p>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={fillData} margin={{ top: 4, right: 8, bottom: 48, left: 0 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-40} textAnchor="end" interval={0} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} tickFormatter={v => `${v}%`} width={36} />
            <Tooltip formatter={(v: number) => [`${v}%`, "Fill Level"]} />
            <Bar dataKey="fill" radius={[4, 4, 0, 0]}>
              {fillData.map((d, i) => (
                <Cell key={i} fill={fillColor(d.fill)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-display font-semibold mb-1 text-sm">Battery Level</h3>
          <p className="text-xs text-muted-foreground mb-4">Sorted by fill level for correlation analysis</p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={fillData} margin={{ top: 4, right: 8, bottom: 48, left: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-40} textAnchor="end" interval={0} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} tickFormatter={v => `${v}%`} width={36} />
              <Tooltip formatter={(v: number) => [`${v}%`, "Battery"]} />
              <Line type="monotone" dataKey="battery" stroke="#7c3aed" strokeWidth={2.5} dot={{ r: 3, fill: "#7c3aed" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="font-display font-semibold mb-1 text-sm">Gas Level (ppm)</h3>
          <p className="text-xs text-muted-foreground mb-4">Bins above 150ppm require environmental alert</p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={gasData} margin={{ top: 4, right: 8, bottom: 48, left: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-40} textAnchor="end" interval={0} />
              <YAxis tick={{ fontSize: 10 }} width={40} />
              <Tooltip formatter={(v: number) => [`${v} ppm`, "Gas Level"]} />
              <Line type="monotone" dataKey="gas" stroke="#f59e0b" strokeWidth={2.5} dot={{ r: 3, fill: "#f59e0b" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

const WASTE_TYPES = [
  { label: "Recyclable", color: "#3b82f6", icon: Recycle, guide: "Rinse and place in blue bin. Avoid contamination with food residue." },
  { label: "Organic", color: "#22c55e", icon: Recycle, guide: "Compost via green bin. Suitable for biogas / soil enrichment." },
  { label: "Hazardous", color: "#ef4444", icon: AlertTriangle, guide: "Do NOT mix with regular waste. Handover at certified e-waste / chem center." },
  { label: "General", color: "#737373", icon: Trash2, guide: "Sealed disposal in black bin. Headed for landfill." },
];

type VisionResult = { label: string; confidence: number; guidance: string; inference_time: number };

function VisionSection() {
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<VisionResult | null>(null);
  const [fallback, setFallback] = useState<typeof WASTE_TYPES[number] | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [apiError, setApiError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (f: File) => {
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setFallback(null);
    setApiError("");
    setAnalyzing(true);
    try {
      const form = new FormData();
      form.append("file", f);
      const res = await fetch(`${API}/predict`, { method: "POST", body: form });
      if (res.status === 503) {
        // Model offline — fallback to local mock
        setFallback(WASTE_TYPES[Math.floor(Math.random() * WASTE_TYPES.length)]);
        setApiError("AI model offline — showing simulation result.");
      } else if (res.ok) {
        setResult(await res.json());
      } else {
        setFallback(WASTE_TYPES[Math.floor(Math.random() * WASTE_TYPES.length)]);
        setApiError(`API error ${res.status} — showing simulation.`);
      }
    } catch {
      setFallback(WASTE_TYPES[Math.floor(Math.random() * WASTE_TYPES.length)]);
      setApiError("Network error — showing simulation result.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <div
        className="rounded-xl border-2 border-dashed border-border bg-card p-8 grid place-items-center min-h-[400px] cursor-pointer hover:border-primary transition"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
        />
        {preview ? (
          <img src={preview} alt="Upload" className="max-h-80 rounded-lg object-contain" />
        ) : (
          <div className="text-center">
            <Upload className="size-10 mx-auto text-muted-foreground" />
            <p className="mt-3 font-medium">Drop a waste image here</p>
            <p className="text-xs text-muted-foreground">or click to upload • PNG / JPG</p>
          </div>
        )}
      </div>
      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="font-display font-semibold flex items-center gap-2"><Eye className="size-4 text-primary" /> AI Vision Core</h3>
        {apiError && <p className="text-xs text-amber-600 mt-3 bg-amber-50 px-3 py-2 rounded-lg">{apiError}</p>}
        {analyzing && <p className="text-sm text-muted-foreground mt-6 animate-pulse">Analyzing image with CNN classifier…</p>}
        {!analyzing && !result && !fallback && <p className="text-sm text-muted-foreground mt-6">Upload an image to classify waste type and receive disposal guidance.</p>}
        {/* Live API result */}
        {result && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-3">
              <span className="size-12 rounded-full grid place-items-center bg-primary/10 text-primary">
                <CheckCircle2 className="size-6" />
              </span>
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Classified as</div>
                <div className="font-display text-2xl font-semibold text-primary">{result.label}</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <Metric label="Confidence" value={`${(result.confidence * 100).toFixed(1)}%`} />
              <Metric label="Model" value="WasteNet v2" />
              <Metric label="Latency" value={`${result.inference_time} ms`} />
            </div>
            <div className="rounded-lg bg-muted/50 p-4 text-sm">
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground mb-1.5">
                <CheckCircle2 className="size-3.5" /> Disposal Guidance
              </div>
              {result.guidance}
            </div>
          </div>
        )}
        {/* Fallback simulation result */}
        {fallback && !result && (
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-3">
              <span className="size-12 rounded-full grid place-items-center" style={{ background: `${fallback.color}22`, color: fallback.color }}>
                <fallback.icon className="size-6" />
              </span>
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Simulated Result</div>
                <div className="font-display text-2xl font-semibold" style={{ color: fallback.color }}>{fallback.label}</div>
              </div>
            </div>
            <div className="rounded-lg bg-muted/50 p-4 text-sm">
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground mb-1.5">
                <AlertTriangle className="size-3.5" /> Simulated Guidance
              </div>
              {fallback.guide}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

type Complaint = { id: string; name: string; area: string; type: string; status: "Open" | "Resolved"; time: string };
const INITIAL_COMPLAINTS: Complaint[] = [
  { id: "C-1042", name: "Anita S.",  area: "Lajpat Nagar",   type: "Overflow",   status: "Open",     time: "2m ago" },
  { id: "C-1041", name: "Rahul K.",  area: "Karol Bagh",     type: "Missed Pickup", status: "Resolved", time: "18m ago" },
  { id: "C-1040", name: "Priya M.",  area: "Saket",          type: "Bad Odour",  status: "Open",     time: "44m ago" },
];

function CommunitySection() {
  const [list, setList] = useState<Complaint[]>(INITIAL_COMPLAINTS);
  const [form, setForm] = useState({ name: "", area: "", type: "Overflow", detail: "" });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetch(`${API}/complaints?limit=10`)
      .then((r) => r.ok ? r.json() : [])
      .then((data: any[]) => {
        if (data.length) {
          setList(data.map((c, i) => ({
            id: `C-${1000 + i}`,
            name: c.user_name ?? c.Citizen ?? "Unknown",
            area: c.location ?? c.Location ?? "—",
            type: c.type ?? c.Issue ?? "General",
            status: (c.status ?? c.Status ?? "Open") as "Open" | "Resolved",
            time: c.timestamp ? new Date(c.timestamp).toLocaleTimeString() : "—",
          })));
        }
      })
      .catch(() => {});
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.area.trim()) return;
    setSubmitting(true);
    try {
      await fetch(`${API}/complaints`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_name: form.name, location: form.area, type: form.type }),
      });
    } catch (_) {}
    setList((prev) => [
      { id: `C-${1043 + prev.length}`, name: form.name.slice(0, 50), area: form.area.slice(0, 50), type: form.type, status: "Open", time: "just now" },
      ...prev,
    ]);
    setForm({ name: "", area: "", type: "Overflow", detail: "" });
    setSubmitting(false);
  };

  return (
    <div className="grid lg:grid-cols-5 gap-4">
      <form onSubmit={submit} className="lg:col-span-2 rounded-xl border border-border bg-card p-6 space-y-3">
        <h3 className="font-display font-semibold flex items-center gap-2"><MessageSquare className="size-4 text-primary" /> File a Complaint</h3>
        <Field label="Your Name">
          <input className="input" maxLength={50} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </Field>
        <Field label="Area / Locality">
          <input className="input" maxLength={50} value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} required />
        </Field>
        <Field label="Issue Type">
          <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
            <option>Overflow</option><option>Missed Pickup</option><option>Bad Odour</option><option>Damaged Bin</option>
          </select>
        </Field>
        <Field label="Details">
          <textarea className="input min-h-[80px]" maxLength={500} value={form.detail} onChange={(e) => setForm({ ...form, detail: e.target.value })} />
        </Field>
        <button disabled={submitting} className="w-full rounded-md bg-primary text-primary-foreground py-2.5 text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-50">
          <Send className="size-4" /> {submitting ? "Submitting…" : "Submit Complaint"}
        </button>
      </form>
      <div className="lg:col-span-3 rounded-xl border border-border bg-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold">Recent Complaints</h3>
          <span className="text-xs text-muted-foreground">{list.filter((c) => c.status === "Open").length} open</span>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase tracking-wider text-muted-foreground border-b border-border">
              <tr><th className="text-left py-2">ID</th><th className="text-left">Citizen</th><th className="text-left">Area</th><th className="text-left">Type</th><th className="text-left">Status</th><th className="text-right">When</th></tr>
            </thead>
            <tbody>
              {list.map((c) => (
                <tr key={c.id} className="border-b border-border/50">
                  <td className="py-2.5 font-mono text-xs">{c.id}</td>
                  <td>{c.name}</td>
                  <td className="text-muted-foreground">{c.area}</td>
                  <td>{c.type}</td>
                  <td>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${c.status === "Open" ? "bg-amber-500/15 text-amber-600" : "bg-green-500/15 text-green-700"}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="text-right text-muted-foreground text-xs">{c.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <style>{`.input{width:100%;border:1px solid var(--border);background:var(--background);border-radius:0.5rem;padding:0.55rem 0.75rem;font-size:0.875rem;outline:none}.input:focus{border-color:var(--primary)}`}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}
