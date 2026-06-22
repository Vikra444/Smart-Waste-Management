import { createFileRoute } from "@tanstack/react-router";
import { Leaf, Target, Users, Award } from "lucide-react";
import heroCity from "@/assets/hero-city.jpg";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — NEUROX" },
      { name: "description", content: "A student-built smart waste management platform combining AI, IoT, and human-centered design for sustainable cities." },
    ],
  }),
  component: About,
});

function About() {
  return (
    <>
      <section className="relative pt-40 pb-24 bg-ink text-ink-foreground overflow-hidden">
        <img src={heroCity} alt="" className="absolute inset-0 size-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-b from-ink/80 to-ink" />
        <div className="relative mx-auto max-w-7xl px-6">
          <span className="text-xs font-semibold tracking-widest text-primary uppercase">About Us</span>
          <h1 className="mt-3 text-5xl md:text-7xl font-bold max-w-4xl">
            Building the operating system for circular cities.
          </h1>
        </div>
      </section>

      <section className="py-24">
        <div className="mx-auto max-w-4xl px-6 prose-lg">
          <p className="text-xl text-muted-foreground leading-relaxed">
            NEUROX started as a student initiative tackling a very real problem: cities
            generate more waste every year, and traditional management systems just can't keep up.
            We believe AI and IoT can change that — bin by bin, route by route, city by city.
          </p>
          <p className="mt-6 text-xl text-muted-foreground leading-relaxed">
            Our platform combines low-cost sensor hardware, computer-vision models, and
            optimization algorithms into a single end-to-end system. It's designed to scale
            from a pilot of 10 bins to a deployment of 10,000+.
          </p>
        </div>
      </section>

      <section className="py-20 bg-secondary">
        <div className="mx-auto max-w-7xl px-6 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {[
            { Icon: Target, t: "Our Mission", d: "Make every city's waste system data-driven, transparent, and sustainable." },
            { Icon: Leaf, t: "Sustainability", d: "Lower emissions, less overflow, higher recycling rates." },
            { Icon: Users, t: "People First", d: "Tools designed for sanitation workers, officials, and citizens alike." },
            { Icon: Award, t: "Built to Win", d: "An academic project engineered for real-world deployment." },
          ].map(({ Icon, t, d }) => (
            <div key={t} className="bg-card rounded-2xl p-7 border border-border">
              <Icon className="text-primary" size={26} />
              <h3 className="mt-4 text-lg font-semibold">{t}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{d}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-24">
        <div className="mx-auto max-w-7xl px-6">
          <h2 className="text-4xl md:text-5xl font-bold">Tech Stack</h2>
          <p className="mt-4 text-muted-foreground text-lg max-w-2xl">
            We pick the right tool for the job — open source where possible, cloud-native by design.
          </p>
          <div className="mt-12 flex flex-wrap gap-3">
            {["ESP32", "Arduino", "LoRa", "Python", "TensorFlow", "OpenCV", "FastAPI", "PostgreSQL", "React", "TanStack", "MQTT", "Docker"].map((tech) => (
              <span key={tech} className="rounded-full bg-secondary border border-border px-5 py-2 text-sm font-medium">{tech}</span>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
