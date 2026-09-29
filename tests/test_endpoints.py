"""
SIH-26227 Test Suite — Endpoint Integration Tests
Exercises all 13 API endpoints against a live TestClient instance.
Run: pytest tests/test_endpoints.py -v
"""

import sys
import io
from pathlib import Path
import numpy as np
from PIL import Image
import pytest

# Ensure project root on path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from project_code.api.app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def _make_image_bytes(h: int = 64, w: int = 64, bright: bool = False) -> bytes:
    arr = np.ones((h, w, 3), dtype=np.uint8) * (220 if bright else 80)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 1. Health
# ---------------------------------------------------------------------------
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "device" in data


# ---------------------------------------------------------------------------
# 2. Datasets
# ---------------------------------------------------------------------------
def test_datasets(client):
    r = client.get("/api/datasets")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# 3. Sample Pairs List
# ---------------------------------------------------------------------------
def test_sample_pairs_list(client):
    r = client.get("/api/sample-pairs")
    assert r.status_code == 200
    pairs = r.json()
    assert isinstance(pairs, list)
    assert len(pairs) >= 1


# ---------------------------------------------------------------------------
# 4. Load Individual Sample Pair
# ---------------------------------------------------------------------------
def test_load_sample_pair(client):
    r = client.get("/api/sample-pair/levir_test_10")
    assert r.status_code == 200
    data = r.json()
    assert data["sample_id"] == "levir_test_10"
    assert data["width"] > 0
    assert data["height"] > 0
    assert data["t1_base64"].startswith("data:image/png;base64,")


def test_load_sample_pair_not_found(client):
    r = client.get("/api/sample-pair/nonexistent_pair")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# 5. Change Detection
# ---------------------------------------------------------------------------
def test_change_detect(client):
    b1 = _make_image_bytes()
    b2 = _make_image_bytes(bright=True)
    r = client.post(
        "/api/change-detect",
        data={"threshold": "0.40", "apply_false_alarm_filter": "true", "model_type": "siamese_resnet18_cbam"},
        files={"file_t1": ("t1.png", b1, "image/png"), "file_t2": ("t2.png", b2, "image/png")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "change_detected" in data
    assert "confidence" in data
    assert data["images"]["mask_base64"].startswith("data:image/png;base64,")


# ---------------------------------------------------------------------------
# 6. Chat Query
# ---------------------------------------------------------------------------
def test_chat_query_text_only(client):
    r = client.post("/api/chat-query", data={"query": "Is there new construction?", "threshold": "0.40"})
    assert r.status_code == 200
    data = r.json()
    assert "response" in data or "text" in data or "message" in data or len(data) > 0


# ---------------------------------------------------------------------------
# 7. Semantic Search
# ---------------------------------------------------------------------------
def test_semantic_search(client):
    r = client.post("/api/semantic-search", json={"query": "new construction near road", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data


# ---------------------------------------------------------------------------
# 8. Active Learning Feedback
# ---------------------------------------------------------------------------
def test_feedback(client):
    r = client.post("/api/feedback", json={"query_text": "urban expansion", "action": "CONFIRM"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "feedback_incorporated"


# ---------------------------------------------------------------------------
# 9. Temporal Bisection
# ---------------------------------------------------------------------------
def test_temporal_bisect(client):
    r = client.post(
        "/api/temporal-bisect",
        json={"sequence_length": 16, "change_onset_index": 7, "change_threshold": 0.5},
    )
    assert r.status_code == 200
    data = r.json()
    assert "earliest_change_timestamp" in data or "earliest" in str(data)


# ---------------------------------------------------------------------------
# 10. Clustering
# ---------------------------------------------------------------------------
def test_clusters(client):
    r = client.get("/api/clusters")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# 11. Analyst Review
# ---------------------------------------------------------------------------
def test_review(client):
    r = client.post(
        "/api/review",
        json={
            "tile_id": "test_tile_001",
            "dataset_name": "LEVIR-CD",
            "action": "CONFIRM",
            "analyst_id": "pytest_user",
            "change_percentage": 9.72,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "logged"
    assert "provenance_hash" in data


# ---------------------------------------------------------------------------
# 12. Audit Logs
# ---------------------------------------------------------------------------
def test_audit_logs(client):
    r = client.get("/api/audit-logs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# 13. GeoJSON Export
# ---------------------------------------------------------------------------
def test_geojson_export(client):
    r = client.get("/api/export-geojson/test_tile_001")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 1
    assert data["features"][0]["geometry"]["type"] == "Polygon"
