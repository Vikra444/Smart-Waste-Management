import { createFileRoute } from "@tanstack/react-router";
import heroCity from "@/assets/hero-city.jpg";
import routeTruck from "@/assets/route-truck.jpg";
import smartBin from "@/assets/smart-bin.jpg";

export const Route = createFileRoute("/use-cases")({
  head: () => ({
    meta: [
      { title: "Use Cases — NEUROX" },
      { name: "description", content: "Real-world applications: municipalities, smart campuses, recycling hubs, and citizen engagement." },
    ],
  }),
  component: UseCases,
});

const cases = [
  { img: heroCity, tag: "Municipality", t: "City-Wide Waste Network", d: "Deploy hundreds of smart bins across districts. Optimize pickup schedules, reduce overflow complaints, and cut diesel costs for the city fleet." },
  { img: routeTruck, tag: "Fleet Operator", t: "Dynamic Route Planning", d: "Replace fixed daily routes with AI-generated routes based on actual bin fill levels — up to 60% fewer kilometers driven." },
  { img: smartBin, tag: "Campus / Corporate", t: "Smart Campus Segregation", d: "Track which bins are misused. Run gamified segregation campaigns. Generate ESG reports automatically." },
  { img: heroCity, tag: "Recycling", t: "Material Recovery Insights", d: "Computer-vision sorting at recycling hubs. Track contamination rates and stream purity across facilities." },
  { img: routeTruck, tag: "Public Health", t: "Overflow & Hazard Alerts", d: "Instant alerts for overflowing bins or fire-risk conditions. Faster response, healthier neighborhoods." },
  { img: smartBin, tag: "Citizens", t: "Report & Reward", d: "Mobile app lets citizens report dumping and earn incentives for proper segregation." },
];

function UseCases() {
  return (
    <>
      <section className="pt-40 pb-20 bg-secondary">
        <div className="mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">Use Cases</span>
          <h1 className="mt-3 text-5xl md:text-7xl font-bold max-w-3xl">From single bins to entire cities.</h1>
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl">
            NEUROX scales from a campus pilot to a city-wide rollout. Here's how different
            stakeholders use the platform.
          </p>
        </div>
      </section>

      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6 space-y-20">
          {cases.map((c, i) => (
            <div key={c.t} className={`grid gap-10 lg:grid-cols-2 items-center ${i % 2 ? "lg:[&>*:first-child]:order-2" : ""}`}>
              <div className="rounded-2xl overflow-hidden aspect-[4/3]">
                <img src={c.img} alt={c.t} loading="lazy" className="size-full object-cover" />
              </div>
              <div>
                <span className="text-xs font-semibold tracking-widest text-primary uppercase">{c.tag}</span>
                <h2 className="mt-3 text-3xl md:text-4xl font-bold">{c.t}</h2>
                <p className="mt-5 text-muted-foreground text-lg">{c.d}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
