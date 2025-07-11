"""Utility helpers for the backend."""

import json

import answer_generator


def summarize_results(results: list[dict]) -> str:
    """Return a human friendly summary for query results."""
    if not results:
        return ""
    try:
        return answer_generator.generate_answer(
            "Summarize these query results in one sentence.", results
        )
    except Exception:
        columns = ", ".join(results[0].keys())
        return columns


def build_fallback_answer(question: str, results: list[dict]) -> str:
    """Return a natural language answer using an LLM as a fallback."""
    if not results:
        return ""
    try:
        return answer_generator.generate_answer(question, results)
    except Exception:
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
