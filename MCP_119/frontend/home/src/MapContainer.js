import React, { useEffect, useRef } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import { fromLonLat } from 'ol/proj';

function MapContainer() {
  const mapRef = useRef(null);

  useEffect(() => {
    const usCenter = fromLonLat([-98.5795, 39.8283]);
    const usExtent = [
      ...fromLonLat([-125, 24]),
      ...fromLonLat([-66, 49]),
    ];

    const map = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: usCenter,
        zoom: 4,
        extent: usExtent,
      }),
    });
    return () => {
      map.setTarget(null);
    };
  }, []);

  return <div ref={mapRef} style={{ width: '100%', height: '400px' }} />;
}

export default MapContainer;
