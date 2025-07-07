import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from utils import results_to_geojson


def test_results_to_geojson_empty():
    assert results_to_geojson([]) is None


def test_results_to_geojson_latlon():
    rows = [{"id": 1, "lat": 10, "lon": 20}]
    geo = results_to_geojson(rows)
    assert geo is not None
    assert geo["features"][0]["geometry"]["coordinates"] == [20, 10]


def test_results_to_geojson_geom_json():
    rows = [{"id": 1, "geom_json": "{\"type\": \"Point\", \"coordinates\": [30, 40]}"}]
    geo = results_to_geojson(rows)
    assert geo is not None
    assert geo["features"][0]["geometry"]["coordinates"] == [30, 40]
