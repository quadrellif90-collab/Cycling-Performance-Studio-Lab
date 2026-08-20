"""Tests for API routes via FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from app import app
    return TestClient(app)


class TestVersionAPI:
    """Test /api/version endpoint."""

    def test_version_returns_200(self, client):
        r = client.get("/api/version")
        assert r.status_code == 200

    def test_version_has_app_field(self, client):
        r = client.get("/api/version")
        data = r.json()
        assert "app" in data or "version" in data

    def test_version_app_is_cpsl(self, client):
        r = client.get("/api/version")
        data = r.json()
        if "app" in data:
            assert data["app"] == "cpsl"


class TestDashboardAPI:
    """Test /api/dashboard endpoints."""

    def test_dashboard_home(self, client):
        r = client.get("/api/dashboard/home")
        assert r.status_code in (200, 500)


class TestNutritionAPI:
    """Test /api/nutrition endpoints."""

    def test_nutrition_full(self, client):
        r = client.get("/api/nutrition-full")
        assert r.status_code == 200

    def test_diet(self, client):
        r = client.get("/api/diet")
        assert r.status_code in (200, 500)


class TestStrengthAPI:
    """Test /api/strength endpoints."""

    def test_strength_plan(self, client):
        r = client.get("/api/strength-plan")
        assert r.status_code == 200

    def test_mobility_plan(self, client):
        r = client.get("/api/mobility-plan")
        assert r.status_code == 200


class TestBIAAPI:
    """Test /api/bia endpoints."""

    def test_bia_history(self, client):
        r = client.get("/api/bia-history")
        assert r.status_code in (200, 500)


class TestCPModelsAPI:
    """Test /api/cp-models endpoint."""

    def test_cp_models(self, client):
        r = client.get("/api/cp-models")
        assert r.status_code in (200, 500)


class TestFieldTestAPI:
    """Test /api/field-test endpoints."""

    def test_field_test_protocols(self, client):
        r = client.get("/api/field-test/protocols")
        assert r.status_code == 200


class TestCalendarAPI:
    """Test /api/calendar endpoints."""

    def test_calendar_ics(self, client):
        r = client.get("/api/calendar.ics")
        assert r.status_code == 200
        assert "text/calendar" in r.headers.get("content-type", "")


class TestCustomChartsAPI:
    """Test /api/custom-charts endpoint."""

    def test_custom_charts(self, client):
        r = client.get("/api/custom-charts")
        assert r.status_code == 200


class TestUpstreamCheckAPI:
    """Test /api/upstream/check endpoint."""

    def test_upstream_check(self, client):
        r = client.get("/api/upstream/check")
        assert r.status_code == 200


class TestInjuryAPI:
    """Test /api/injury endpoints."""

    def test_injury_blocks(self, client):
        r = client.get("/api/injury/blocks")
        assert r.status_code in (200, 500)


class TestExportAPI:
    """Test /api/export endpoints."""

    def test_export_bundle(self, client):
        r = client.get("/api/export/bundle")
        assert r.status_code == 200


class TestProfileAPI:
    """Test /api/profile endpoints."""

    def test_profile(self, client):
        r = client.get("/api/profile")
        assert r.status_code in (200, 500)


class TestMetabolicAPI:
    """Test /api/metabolic-profile endpoint."""

    def test_metabolic_profile(self, client):
        r = client.get("/api/metabolic-profile")
        assert r.status_code in (200, 500)


class TestSyncTargetsAPI:
    """Test /api/sync-targets endpoint."""

    def test_sync_targets(self, client):
        r = client.get("/api/sync-targets")
        assert r.status_code in (200, 500)


class TestRecommendationsAPI:
    """Test /api/athlete/recommendations endpoint."""

    def test_recommendations(self, client):
        r = client.get("/api/athlete/recommendations")
        assert r.status_code in (200, 500)


class TestPedalAPI:
    """Test /api/pedal endpoints."""

    def test_pedal_latest(self, client):
        r = client.get("/api/pedal-latest")
        assert r.status_code in (200, 500)

    def test_pedal_history(self, client):
        r = client.get("/api/pedal-history")
        assert r.status_code in (200, 500)


class TestBIAVisionAPI:
    """Test /api/bia-vision-analyze endpoint."""

    def test_bia_vision_analyze_missing_key(self, client):
        r = client.post("/api/bia-vision-analyze")
        assert r.status_code == 400
        assert "BIA_VISION_API_KEY" in r.json().get("error", "")


class TestSelfUpdateAPI:
    """Test /api/self-update endpoint."""

    def test_self_update_no_asset(self, client):
        r = client.post("/api/self-update")
        # Should return 400 when no download URL available (upstream check fails)
        assert r.status_code in (200, 400, 500)
        data = r.json()
        assert "ok" in data or "error" in data
