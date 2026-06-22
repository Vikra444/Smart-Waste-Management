import { useEffect, useState, lazy, Suspense } from "react";

// Lazy-loaded client component to isolate Leaflet map instantiation from SSR node environments
const LeafletMap = lazy(() => import("./LeafletMap"));

export type Bin = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  fill: number;
  battery: number;
  temp: number;
  gas: number;
  isReal?: boolean;
};

export function fillColor(fill: number) {
  if (fill >= 80) return "#ef4444";
  if (fill >= 60) return "#f59e0b";
  return "#22c55e";
}

export function CityMap({ bins, route }: { bins: Bin[]; route: [number, number][] }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-full w-full bg-muted animate-pulse rounded-xl" />;
  }

  return (
    <Suspense fallback={<div className="h-full w-full bg-muted animate-pulse rounded-xl" />}>
      <LeafletMap bins={bins} route={route} />
    </Suspense>
  );
}
