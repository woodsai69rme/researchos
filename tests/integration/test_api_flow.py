"""
Integration Tests for ResearchOS FastAPI Endpoints & Deep Research Execution
"""
import pytest
from fastapi.testclient import TestClient
from researchos.apps.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app"] == "ResearchOS"
    assert data["free_only_enforced"] is True
    assert data["default_currency"] == "AUD"


def test_models_catalog_endpoint(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 3
    assert any(m["model_id"] == "ornith-1.0-35b:q4_k_m" for m in models)


def test_video_costs_endpoint(client):
    response = client.get("/api/video-costs?minutes=3.5")
    assert response.status_code == 200
    costs = response.json()
    assert len(costs) >= 4
    # Local Wan 2.2 should have $0.00 cost
    assert any(v["provider_name"] == "Wan 2.2 Mega (Local ComfyUI)" and v["estimated_total_music_video_cost_aud"] == 0.0 for v in costs)


def test_automotive_specs_endpoint(client):
    response = client.get("/api/automotive/spec?query=XR6+Turbo+TH400")
    assert response.status_code == 200
    specs = response.json()
    assert specs["fitment_status"] == "Compatible with Conversion Kit"
    assert "gearbox" in specs["component_breakdown"]


def test_research_execute_end_to_end(client):
    req_payload = {
        "query": "Find the best free AI coding setup with SWE-bench verified models",
        "mode": "FREE_ONLY",
        "depth": "normal",
        "location": "Brisbane, Queensland, Australia",
        "budget": 0.0,
        "monitor_interval": 12,
    }
    response = client.post("/api/research/execute", json=req_payload)
    assert response.status_code == 200
    report = response.json()

    assert report["operating_mode"] == "FREE_ONLY"
    assert report["actual_spend_aud"] == 0.0
    assert report["paid_providers_executed"] == 0
    assert len(report["free_options"]) >= 1
    assert len(report["what_you_missed"]) >= 1
    assert len(report["promotions"]) >= 1
    assert report["confidence_score"] >= 0.8
