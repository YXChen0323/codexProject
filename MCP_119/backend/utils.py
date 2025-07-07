"""Utility helpers for the backend."""

import json


def summarize_results(results: list[dict]) -> str:
    """Return a short human friendly summary for query results."""
    if not results:
        return "沒有任何資料。"
    row_count = len(results)
    columns = ", ".join(results[0].keys())
    return f"共 {row_count} 筆資料，欄位包含 {columns}。"


def results_to_geojson(rows: list[dict]) -> dict | None:
    """Convert query results to a GeoJSON FeatureCollection if possible."""
    features = []
    for row in rows:
        props = dict(row)
        geometry = None
        geom_json = props.pop("geom_json", None) or props.pop("geojson", None)
        if geom_json:
            try:
                geometry = json.loads(geom_json)
            except Exception:
                geometry = None
        if geometry is None:
            lat = None
            lon = None
            for k in ("latitude", "lat", "y"):
                if k in props and props[k] is not None:
                    try:
                        lat = float(props.pop(k))
                        break
                    except (TypeError, ValueError):
                        pass
            for k in ("longitude", "lon", "lng", "x"):
                if k in props and props[k] is not None:
                    try:
                        lon = float(props.pop(k))
                        break
                    except (TypeError, ValueError):
                        pass
            if lat is not None and lon is not None:
                geometry = {"type": "Point", "coordinates": [lon, lat]}
        if geometry:
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": props,
            })
    if features:
        return {"type": "FeatureCollection", "features": features}
    return None
