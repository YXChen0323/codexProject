import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
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

function MapView({ data }) {
  const markers = data
    .map((row) => ({ row, latlng: getLatLng(row) }))
    .filter((m) => m.latlng);
  if (markers.length === 0) return null;
  const center = markers[0].latlng;
  return (
    <div className="h-96 w-full my-4">
      <MapContainer center={center} zoom={13} className="h-full w-full">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
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
