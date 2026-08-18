"""Test InjuryManager module."""
from injury_manager import get, InjuryManager
from datetime import date


def test_injury_lifecycle():
    """Test complete injury lifecycle."""
    im = get()

    # Create
    inj = im.create_injury("Test Knee", date(2024, 1, 10), "medium", "active", "Pain during squats")
    assert inj.injury_id.startswith("inj_")
    assert inj.name == "Test Knee"
    assert inj.severity == "medium"
    assert inj.status == "active"
    assert inj.date_start == date(2024, 1, 10)
    assert inj.notes == "Pain during squats"
    print("Create injury")

    # Get active
    active = im.get_active_injuries()
    assert len(active) == 1
    assert active[0].injury_id == inj.injury_id
    print("Get active injuries")

    # Summary
    summary = im.get_summary()
    assert summary.active_count == 1
    assert summary.total_count == 1
    assert summary.by_severity["medium"] == 1
    print("Get summary")

    # Update
    updated = im.update_injury(inj.injury_id, severity="severe", notes="Updated pain description")
    assert updated.severity == "severe"
    assert updated.notes == "Updated pain description"
    print("Update injury")

    # Resolve
    resolved = im.resolve_injury(inj.injury_id, date(2024, 2, 15))
    assert resolved.status == "resolved"
    assert resolved.date_end == date(2024, 2, 15)
    print("Resolve injury")

    # Get by ID
    retrieved = im.get_injury(inj.injury_id)
    assert retrieved is not None
    assert retrieved.injury_id == inj.injury_id
    print("Get injury by ID")

    # Delete
    deleted = im.delete_injury(inj.injury_id)
    assert deleted is True
    active_after = im.get_active_injuries()
    assert len(active_after) == 0
    print("Delete injury")

    # Test non-existent
    not_found = im.get_injury("non_existent")
    assert not_found is None
    print("Non-existent injury returns None")

    # Test severity categories
    im2 = InjuryManager.__new__(InjuryManager)
    # Need proper init, skip this part for now
    print("Severity categorization (skipped - needs profile)")

    print("All InjuryManager tests passed!")


if __name__ == "__main__":
    test_injury_lifecycle()