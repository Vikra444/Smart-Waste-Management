import { MapContainer, TileLayer, CircleMarker, Tooltip, Polyline, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { type Bin, fillColor } from "./CityMap";

export default function LeafletMap({ bins, route }: { bins: Bin[]; route: [number, number][] }) {
  const center: [number, number] = [bins[0]?.lat ?? 28.6139, bins[0]?.lng ?? 77.209];

  return (
    <MapContainer center={center} zoom={13} className="h-full w-full rounded-xl z-0" scrollWheelZoom>
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {bins.flatMap((b) => [
        b.isReal && (
          <Circle
            key={`${b.id}-ring`}
            center={[b.lat, b.lng]}
            radius={120}
            pathOptions={{ color: "#22d3ee", weight: 2, fillColor: "#22d3ee", fillOpacity: 0.12 }}
          />
        ),
        <CircleMarker
          key={b.id}
          center={[b.lat, b.lng]}
          radius={10}
          pathOptions={{ color: "#0f172a", weight: 1.5, fillColor: fillColor(b.fill), fillOpacity: 0.9 }}
        >
          <Tooltip direction="top" offset={[0, -8]}>
            <div className="text-xs">
              <div className="font-semibold">{b.name}</div>
              <div>Fill: {b.fill.toFixed(0)}% • Bat: {b.battery.toFixed(0)}%</div>
              <div>Temp: {b.temp.toFixed(1)}°C • Gas: {b.gas.toFixed(1)} ppm</div>
              {b.isReal && <div className="text-cyan-600 font-medium">● Real IoT Device</div>}
            </div>
          </Tooltip>
        </CircleMarker>,
      ])}
      {route.length > 1 && (
        <Polyline positions={route} pathOptions={{ color: "#0ea5e9", weight: 3, dashArray: "8 8" }} />
      )}
    </MapContainer>
  );
}
