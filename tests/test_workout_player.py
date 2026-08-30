"""
Tests for the workout_player module.
"""
import tempfile
import time
from pathlib import Path

import pytest


class TestZWOParser:
    """Tests for ZWO workout file parsing."""

    @pytest.fixture
    def sample_zwo_str(self):
        return """<?xml version='1.0' encoding='UTF-8'?>
<workout_file>
    <author>Test Author</author>
    <name>Test Workout</name>
    <description>A test workout</description>
    <sportType>bike</sportType>
    <workout>
        <Warmup Duration="300" PowerLow="0.55" PowerHigh="0.75" />
        <SteadyState Duration="300" Power="0.9" />
        <Cooldown Duration="300" PowerLow="0.65" PowerHigh="0.45" />
    </workout>
</workout_file>"""

    @pytest.fixture
    def sample_zwo_file(self, sample_zwo_str):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".zwo", delete=False) as f:
            f.write(sample_zwo_str)
            f.flush()
            path = Path(f.name)
        yield path
        path.unlink(missing_ok=True)

    def test_parse_basic_workout(self, sample_zwo_file):
        from workout_player import IntervalType, ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=300.0)

        assert timeline.name == "Test Workout"
        assert timeline.description == "A test workout"
        assert timeline.author == "Test Author"
        assert timeline.ftp == 300.0
        assert timeline.duration_total == pytest.approx(900.0)  # 300+300+300
        assert len(timeline.intervals) == 3
        assert timeline.intervals[0].interval_type == IntervalType.WARMUP
        assert timeline.intervals[1].interval_type == IntervalType.STEADY
        assert timeline.intervals[2].interval_type == IntervalType.COOLDOWN

    def test_parse_warmup_interval(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=250.0)
        warmup = timeline.intervals[0]

        assert warmup.duration == 300
        assert warmup.power_low == 0.55
        assert warmup.power_high == 0.75

    def test_parse_steady_state(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=250.0)
        steady = timeline.intervals[1]

        assert steady.duration == 300
        assert steady.power == 0.9

    def test_get_target_at_time_warmup(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=300.0)
        # At 150s into the 300s warmup, we should be halfway between 0.55 and 0.75
        target, interval = timeline.get_target_at_time(150)
        expected = 0.55 + (0.75 - 0.55) * 0.5  # 0.65
        assert target == pytest.approx(expected, abs=0.01)

    def test_get_target_at_time_steady(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=300.0)
        # At 450s (150s into the steady state interval)
        target, interval = timeline.get_target_at_time(450)
        assert target == pytest.approx(0.9, abs=0.01)

    def test_get_target_at_time_out_of_bounds(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=300.0)
        target, interval = timeline.get_target_at_time(1000)
        assert target == 0.0
        assert interval is None

    def test_intervals_summary(self, sample_zwo_file):
        from workout_player import ZWOParser

        timeline = ZWOParser.parse(sample_zwo_file, ftp=250.0)
        summary = timeline.get_intervals_summary()

        assert len(summary) == 3
        assert summary[0]["type"] == "warmup"
        assert summary[1]["type"] == "steady"
        assert summary[2]["type"] == "cooldown"
        assert summary[0]["name"].startswith("Warmup")


class TestWorkoutPlayerSession:
    """Tests for playback state management."""

    @pytest.fixture
    def sample_timeline(self):
        from workout_player import Interval, IntervalType, WorkoutTimeline

        timeline = WorkoutTimeline(
            name="Test",
            description="Test workout",
            author="Test",
            duration_total=900.0,
            ftp=250.0,
        )
        timeline.intervals = [
            Interval(0, 0.0, 300.0, power_low=0.55, power_high=0.75, interval_type=IntervalType.WARMUP, name="Warmup"),
            Interval(1, 300.0, 300.0, power=0.9, interval_type=IntervalType.STEADY, name="Main Set"),
            Interval(2, 600.0, 300.0, power_low=0.65, power_high=0.45, interval_type=IntervalType.COOLDOWN, name="Cooldown"),
        ]
        return timeline

    def test_session_start_pause_stop(self, sample_timeline):
        from workout_player import PlaybackState, WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        assert session.status.state == PlaybackState.IDLE

        session.start()
        assert session.status.state == PlaybackState.RUNNING
        assert session.status.started_at is not None

        session.pause()
        assert session.status.state == PlaybackState.PAUSED

        session.stop()
        assert session.status.state == PlaybackState.IDLE
        assert session.status.elapsed == 0.0

    def test_session_set_intensity(self, sample_timeline):
        from workout_player import WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        session.set_intensity(0.85)
        assert session.status.intensity_pct == 0.85

        # Test that intensity affects target power
        session.skip_to_time(450)  # Into steady state
        session._update_target()
        # Target should be 0.9 * 0.85 = 0.765
        assert session.status.target_power == pytest.approx(0.765, abs=0.01)

    def test_session_skip_to_time(self, sample_timeline):
        from workout_player import WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        session.skip_to_time(450)
        assert session.status.elapsed == pytest.approx(450, abs=0.1)

    def test_session_report_power(self, sample_timeline):
        from workout_player import WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        session.report_power(200)
        assert session.status.current_power == 200
        assert len(session.status.power_history) == 1

    def test_session_get_status(self, sample_timeline):
        from workout_player import WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        status = session.get_status()

        assert "state" in status
        assert "elapsed" in status
        assert "current_power" in status
        assert "target_power" in status
        assert "interval_index" in status
        assert "intensity_pct" in status
        assert "workout_name" in status
        assert status["workout_name"] == "Test"

    def test_session_skip_interval(self, sample_timeline):
        from workout_player import WorkoutPlayerSession

        session = WorkoutPlayerSession(sample_timeline)
        session.start()
        time.sleep(0.2)  # Let it start running
        session.skip_interval(1)
        assert session.status.interval_index == 1
        session.stop()


class TestTrainerController:
    """Tests for trainer control abstraction."""

    def test_trainer_controller_base(self):
        from workout_player import TrainerController

        trainer = TrainerController(trainer_id="test123")
        assert trainer.trainer_id == "test123"
        assert not trainer.is_connected

        status = trainer.get_status()
        assert status["connected"] is False
        assert status["target_power"] == 0.0

    def test_trainer_disconnect(self):
        from workout_player import TrainerController

        trainer = TrainerController(trainer_id="test456")
        trainer._target_power = 250.0
        trainer.disconnect()
        assert trainer.is_connected is False

    def test_trainer_set_target_power(self):
        from workout_player import TrainerController

        trainer = TrainerController(trainer_id="test789")
        trainer.set_target_power(300.0)
        assert trainer._target_power == 300.0

    def test_ble_trainer_simulated_connect(self):
        from workout_player import BLETrainer

        trainer = BLETrainer(trainer_id="ble001", address="AA:BB:CC:DD:EE")
        # Should succeed (simulated connection)
        result = trainer.connect()
        assert result is True
        assert trainer.is_connected is True

    def test_ant_trainer_import_guard(self):
        from workout_player import ANTPlusTrainer

        trainer = ANTPlusTrainer(trainer_id="ant001", device_number=12345)
        result = trainer.connect()
        # Should return False if openant not available (likely in test env)
        # or True if it connects
        assert isinstance(result, bool)


class TestWorkoutRegistry:
    """Tests for the workout session registry."""

    def test_registry_singleton(self):
        from workout_player import WorkoutRegistry

        r1 = WorkoutRegistry.get()
        r2 = WorkoutRegistry.get()
        assert r1 is r2

    def test_registry_create_and_get_session(self):
        from workout_player import WorkoutRegistry, WorkoutTimeline

        registry = WorkoutRegistry.get()
        timeline = WorkoutTimeline(
            name="Test", description="", author="Test", duration_total=600, ftp=250.0
        )

        session = registry.create_session(timeline, session_id="test_session_1")
        assert session is not None

        retrieved = registry.get_session("test_session_1")
        assert retrieved is session

        registry.end_session("test_session_1")
        assert registry.get_session("test_session_1") is None

    def test_registry_register_trainer(self):
        from workout_player import TrainerController, WorkoutRegistry

        registry = WorkoutRegistry.get()
        trainer = TrainerController(trainer_id="reg_trainer")
        trainer_id = registry.register_trainer(trainer)
        assert trainer_id == "reg_trainer"

        retrieved = registry.get_trainer("reg_trainer")
        assert retrieved is trainer

        trainers = registry.list_trainers()
        assert len(trainers) >= 1

        registry._connected_trainers.pop("reg_trainer", None)


class TestResolveWorkoutPath:
    """Tests for workout path resolution."""

    def test_resolve_workout_path_existing(self):
        from workout_player import resolve_workout_path

        # This will find an actual zwo file in the workouts directory
        result = resolve_workout_path("z2_2x5min_90pct_64min.zwo")
        assert result is not None
        assert result.suffix == ".zwo"

    def test_resolve_workout_path_nonexistent(self):
        from workout_player import resolve_workout_path

        result = resolve_workout_path("nonexistent_workout.zwo")
        assert result is None


class TestFullIntegration:
    """Integration test using a real workout file."""

    def test_parse_real_zwo(self):
        from workout_player import ZWOParser, resolve_workout_path

        path = resolve_workout_path("z2_2x5min_90pct_64min.zwo")
        if path:
            timeline = ZWOParser.parse(path, ftp=250.0)
            assert timeline.name
            assert len(timeline.intervals) > 0
            assert timeline.duration_total > 0

    def test_workout_player_lifecycle(self):
        from workout_player import (
            PlaybackState,
            WorkoutPlayerSession,
            ZWOParser,
            resolve_workout_path,
        )

        path = resolve_workout_path("z2_2x5min_90pct_64min.zwo")
        if path:
            timeline = ZWOParser.parse(path, ftp=250.0)
            session = WorkoutPlayerSession(timeline)

            session.start()
            assert session.status.state == PlaybackState.RUNNING
            time.sleep(0.5)
            session.skip_to_time(timeline.duration_total / 2)
            status = session.get_status()
            assert status["elapsed"] == pytest.approx(timeline.duration_total / 2, abs=1)

            session.stop()
            assert session.status.state == PlaybackState.IDLE
