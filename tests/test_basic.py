"""Basic tests for Cycling Performance Studio Lab."""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all core modules can be imported."""
    from profile_manager import ProfileManager, get
    from error_codes import Codes, REGISTRY, is_valid_code, metadata, all_codes
    from sync_targets import get_target, list_targets, SyncTarget, IntervalsIcuTarget
    from config import config
    from log_config import setup_logging

    # Test profile manager
    pm = get()
    assert pm is not None, "ProfileManager singleton not working"
    assert hasattr(pm, 'list_profiles'), "Missing list_profiles method"
    assert hasattr(pm, 'create_profile'), "Missing create_profile method"
    assert hasattr(pm, 'save_athlete'), "Missing save_athlete method"
    assert hasattr(pm, 'switch'), "Missing switch method"

    # Test error codes
    assert len(REGISTRY) > 0, "No error codes registered"
    assert is_valid_code("E_PROFILE_LOAD"), "E_PROFILE_LOAD not valid"
    meta = metadata("E_PROFILE_LOAD")
    assert meta is not None, "metadata() returned None"
    assert "severity" in meta, "metadata missing severity"
    assert "description" in meta, "metadata missing description"

    # Test all_codes returns sorted list
    codes = all_codes()
    assert codes == sorted(codes), "all_codes() not sorted"

    # Test sync targets
    targets = list_targets()
    assert len(targets) >= 1, "No sync targets registered"
    icu_target = get_target("intervals_icu")
    assert icu_target is not None, "Intervals.icu target not found"
    assert icu_target.key == "intervals_icu", "Wrong key for ICU target"
    assert icu_target.is_configured() == False, "ICU should not be configured by default"

    # Test config
    assert config is not None, "config not loaded"

    # Test individual code lookup
    assert Codes.PLAN_PARSE_CORRUPT == "E_PLAN_PARSE_CORRUPT"
    assert Codes.PROFILE_LOAD == "E_PROFILE_LOAD"

    print("All basic tests passed!")


def test_atomic_writes():
    """Test atomic file write pattern."""
    from profile_manager import ProfileManager

    # Create a temp profile dir
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        prof_dir = Path(tmpdir) / "profiles"
        prof_dir.mkdir()

        pm = ProfileManager.__new__(ProfileManager)
        pm._data_dir = Path(tmpdir)
        pm._profiles_dir = prof_dir
        pm._profiles_dir.mkdir(parents=True, exist_ok=True)
        pm._active_id = None
        pm._lock = __import__('threading').RLock()
        pm._switch_lock = __import__('threading').Lock()
        pm._library_rows_lock = __import__('threading').Lock()
        pm._library_tags_lock = __import__('threading').Lock()

        # Test atomic write
        test_data = {"test": "value", "number": 42}
        pm._atomic_write_json(prof_dir / "test.json", test_data)

        # Verify file was written
        assert (prof_dir / "test.json").exists(), "Atomic write failed"
        content = json.loads((prof_dir / "test.json").read_text())
        assert content == test_data, f"Written data mismatch: {content} != {test_data}"

        # Test atomic env write
        pm._atomic_write_env(prof_dir / ".env", {"KEY": "value"})
        assert (prof_dir / ".env").exists(), "Atomic env write failed"
        env_content = (prof_dir / ".env").read_text()
        assert "KEY=value" in env_content, f"Env content mismatch: {env_content}"

    print("Atomic write tests passed!")


def test_profile_lifecycle():
    """Test profile creation and basic lifecycle."""
    from profile_manager import ProfileManager, get

    pm = get()

    # Create a profile
    pid = pm.create_profile("test-profilo", "blue")
    assert pid is not None, "Profile creation failed"
    assert pid.startswith("test-profilo"), f"Wrong profile ID: {pid}"

    # List profiles
    profiles = pm.list_profiles()
    assert any(p == pid for p in profiles), f"Created profile not in list: {profiles}"

    # Switch to the new profile
    pm.switch(pid)
    assert pm._active_id == pid, f"Failed to switch profile: {pm._active_id}"

    # Verify athlete.json was created
    athlete = pm._load_athlete_json(pid)
    assert athlete is not None, "athlete.json not created"
    assert athlete["ftp"] == 200, f"Wrong FTP: {athlete.get('ftp')}"
    assert athlete["weight_kg"] == 70, f"Wrong weight: {athlete.get('weight_kg')}"

    # Save athlete data
    pm.save_athlete({"ftp": 250, "weight_kg": 75, "lthr": 185, "max_hr": 195})
    athlete = pm._load_athlete_json(pid)
    assert athlete["ftp"] == 250, f"FTP not updated: {athlete.get('ftp')}"
    assert athlete["weight_kg"] == 75, f"Weight not updated: {athlete.get('weight_kg')}"

    # Test validation - FTP out of range should raise
    try:
        pm.save_athlete({"ftp": 1000, "weight_kg": 75})
        assert False, "Should have raised ValueError for FTP out of range"
    except ValueError as e:
        assert "FTP out of range" in str(e), f"Wrong error message: {e}"

    # Test switch
    pm.switch(pid)
    assert pm._active_id == pid, f"Failed to switch profile: {pm._active_id}"

    # Delete profile
    pm.delete_profile(pid)
    profiles = pm.list_profiles()
    assert pid not in profiles, f"Profile not deleted: {profiles}"

    print("Profile lifecycle tests passed!")


if __name__ == "__main__":
    test_imports()
    test_atomic_writes()
    test_profile_lifecycle()