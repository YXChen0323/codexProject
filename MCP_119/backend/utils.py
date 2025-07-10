"""Utility helpers for the backend."""

import json


def summarize_results(results: list[dict]) -> str:
    """Return a short summary for query results or an empty string."""
    # Some deployments prefer not to expose human friendly messages.
    # When this behaviour is desired simply return an empty string.
    if not results:
        return ""
    columns = ", ".join(results[0].keys())
    return columns


def build_fallback_answer(question: str, results: list[dict]) -> str:
    """Return a basic fallback answer or an empty string."""
    # These responses can be suppressed by returning an empty string.
    if not results:
        return ""
    columns = ", ".join(results[0].keys())
    return columns


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
