"""CPSL test fixtures — hermetic, no live network, no real HOME."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Redirect HOME to temp dir before any project imports
_real_home = os.path.expanduser("~")
CPSL_SANDBOX = tempfile.mkdtemp(prefix="cpsl_test_")
os.environ["HOME"] = CPSL_SANDBOX
os.environ["DOMESTIQUE_NO_NET"] = "1"

# Ensure the project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


@pytest.fixture(autouse=True)
def _restore_home():
    """Restore HOME after each test."""
    yield
    os.environ["HOME"] = _real_home


@pytest.fixture(autouse=True)
def _block_live_network():
    """Block all live HTTP during tests."""
    import urllib.request
    orig = urllib.request.urlopen

    def _fake_urlopen(*args, **kwargs):
        raise OSError("Network blocked in tests")

    urllib.request.urlopen = _fake_urlopen
    yield
    urllib.request.urlopen = orig


@pytest.fixture
def tmp_data(tmp_path):
    """Create a temporary data directory with common structure."""
    (tmp_path / "profiles").mkdir()
    (tmp_path / "gpx").mkdir()
    (tmp_path / "workouts").mkdir()
    return tmp_path


@pytest.fixture
def mock_metrics():
    """Return a fixed metrics dict for deterministic tests."""
    return {
        "ftp": 250,
        "hr_max": 190,
        "hr_rest": 55,
        "weight_kg": 75.0,
        "age": 30,
        "sex": "m",
        "height_cm": 180,
    }
