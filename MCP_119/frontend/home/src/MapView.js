import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function getLatLng(row) {
  const latKeys = ['latitude', 'lat', 'y'];
  const lngKeys = ['longitude', 'lon', 'lng', 'x'];
  let lat;
  for (const k of latKeys) {
    if (row[k] !== undefined && row[k] !== null) {
      lat = parseFloat(row[k]);
      break;
    }
  }
  let lng;
  for (const k of lngKeys) {
    if (row[k] !== undefined && row[k] !== null) {
      lng = parseFloat(row[k]);
      break;
    }
  }
  if (lat != null && lng != null) return [lat, lng];
  if (row.geom) {
    const m = String(row.geom).match(/POINT\(([-\d.]+) ([-\d.]+)\)/);
    if (m) return [parseFloat(m[2]), parseFloat(m[1])];
  }
  return null;
}

function MapView({ data = [], geojson }) {
  const markers = Array.isArray(data)
    ? data.map((row) => ({ row, latlng: getLatLng(row) })).filter((m) => m.latlng)
    : [];
  let center = null;
  if (geojson && geojson.features && geojson.features.length > 0) {
    const first = geojson.features[0];
    let c;
    if (first.geometry.type === 'Point') {
      c = first.geometry.coordinates;
    } else if (first.geometry.type === 'LineString') {
      c = first.geometry.coordinates[0];
    } else if (first.geometry.type === 'Polygon') {
      c = first.geometry.coordinates[0][0];
    }
    if (Array.isArray(c)) {
      center = [c[1], c[0]];
    }
  }
  if (!center && markers.length > 0) {
    center = markers[0].latlng;
  }
  if (!center) return null;
  return (
    <div className="h-96 w-full my-4">
      <MapContainer center={center} zoom={13} className="h-full w-full">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {geojson && <GeoJSON data={geojson} />}
        {markers.map((m, idx) => (
          <Marker position={m.latlng} key={idx}>
            <Popup>
              {Object.entries(m.row).map(([k, v]) => (
                <div key={k}>{k}: {String(v)}</div>
              ))}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default MapView;
