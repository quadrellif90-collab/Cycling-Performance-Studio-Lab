"""Tests for utility, infrastructure, and data modules."""


class TestCalendarICS:
    """Test calendar_ics.py — ICS calendar generation."""

    def test_build_ics_returns_string(self):
        from calendar_ics import build_ics
        ics = build_ics()
        assert isinstance(ics, str)

    def test_build_ics_has_header(self):
        from calendar_ics import build_ics
        ics = build_ics()
        assert "VCALENDAR" in ics or "BEGIN:VCALENDAR" in ics


class TestFieldTestProtocols:
    """Test field_test_protocols.py — CP test protocols."""

    def test_list_protocols_count(self):
        from field_test_protocols import list_protocols
        p = list_protocols()
        assert len(p) >= 3

    def test_list_protocols_have_ids(self):
        from field_test_protocols import list_protocols
        p = list_protocols()
        assert all("id" in x for x in p)
        assert all("label" in x for x in p)


class TestCustomCharts:
    """Test custom_charts.py — custom chart builder."""

    def test_load_charts_empty(self):
        from custom_charts import load_charts
        charts = load_charts()
        assert isinstance(charts, list)

    def test_save_charts(self):
        from custom_charts import load_charts, save_charts
        charts = load_charts()
        save_charts(charts)
        assert load_charts() == charts

    def test_upsert_chart(self):
        from custom_charts import load_charts, upsert_chart
        chart = {"id": "test-1", "type": "scatter", "x_metric": "power", "y_metric": "hr"}
        upsert_chart(chart)
        charts = load_charts()
        assert any(c.get("id") == "test-1" for c in charts)


class TestGPXParser:
    """Test gpx_parser.py — GPX file parsing."""

    def test_import(self):
        import gpx_parser
        assert hasattr(gpx_parser, 'parse_gpx')


class TestPlanExport:
    """Test plan_export.py — plan export."""

    def test_import(self):
        import plan_export
        assert hasattr(plan_export, 'build_plan_html')

    def test_build_plan_html(self):
        from plan_export import build_plan_html
        assert callable(build_plan_html)


class TestPlanOptions:
    """Test plan_options.py — plan configuration options."""

    def test_import(self):
        import plan_options
        assert hasattr(plan_options, 'PlanOptions')


class TestMyProgress:
    """Test my_progress.py — progress tracking."""

    def test_import(self):
        import my_progress
        assert hasattr(my_progress, 'compute_my_adherence')

    def test_compute_my_adherence(self):
        from my_progress import compute_my_adherence
        assert callable(compute_my_adherence)


class TestNotifications:
    """Test notifications.py — notification system."""

    def test_import(self):
        import notifications
        assert hasattr(notifications, 'NotificationEngine')

    def test_render_functions(self):
        from notifications import (
            render_morning_readiness,
            render_pr_detect,
            render_weekly_review,
            render_workout_of_day,
        )
        assert callable(render_morning_readiness)
        assert callable(render_workout_of_day)
        assert callable(render_pr_detect)
        assert callable(render_weekly_review)


class TestRunWeb:
    """Test run_web.py — web server launcher."""

    def test_import(self):
        import run_web
        assert hasattr(run_web, 'main')


class TestDataExport:
    """Test data_export.py — data export."""

    def test_import(self):
        import data_export
        assert hasattr(data_export, 'build_bundle')

    def test_build_bundle(self):
        from data_export import build_bundle
        assert callable(build_bundle)

    def test_build_metrics_csv(self):
        from data_export import build_metrics_csv
        assert callable(build_metrics_csv)


class TestInjuryManager:
    """Test injury_manager.py — injury tracking."""

    def test_import(self):
        import injury_manager
        assert hasattr(injury_manager, 'load_blocks')

    def test_load_blocks(self):
        from injury_manager import load_blocks
        assert callable(load_blocks)

    def test_save_block(self):
        from injury_manager import save_block
        assert callable(save_block)


class TestSessionManager:
    """Test session_manager.py — session management."""

    def test_import(self):
        import session_manager
        assert hasattr(session_manager, 'get_session_manager')

    def test_singleton(self):
        from session_manager import get_session_manager
        s1 = get_session_manager()
        s2 = get_session_manager()
        assert s1 is s2


class TestCaching:
    """Test caching.py — TTL cache."""

    def test_import(self):
        import caching
        assert hasattr(caching, 'TTLCache')


class TestSyncTargets:
    """Test sync_targets.py — ICU sync targets."""

    def test_import(self):
        import sync_targets
        assert hasattr(sync_targets, 'list_targets')

    def test_list_targets(self):
        from sync_targets import list_targets
        targets = list_targets()
        assert isinstance(targets, list)

    def test_get_target(self):
        from sync_targets import get_target
        target = get_target("intervals_icu")
        assert target is not None


class TestConfig:
    """Test config.py — configuration."""

    def test_import(self):
        import config
        assert hasattr(config, 'ICU_BASE')

    def test_plan_constants(self):
        from config import WEEKLY_HIT_PCT, WEEKLY_LIT_PCT
        assert isinstance(WEEKLY_LIT_PCT, (int, float))
        assert isinstance(WEEKLY_HIT_PCT, (int, float))


class TestLogConfig:
    """Test log_config.py — logging configuration."""

    def test_import(self):
        import log_config
        assert hasattr(log_config, 'setup_logging')
