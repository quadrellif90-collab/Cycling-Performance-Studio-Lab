"""Tests for nutrition, diet, and BIA modules."""
import pytest


class TestNutrition:
    """Test nutrition.py — macros, supplements, targets."""

    def test_day_macros_high_intensity(self):
        from nutrition import day_macros
        r = day_macros("high_intensity", "maintain", 75, 180, 30, "m")
        assert r["target_kcal"] > 2000
        assert r["carb_g"] > r["fat_g"]

    def test_day_macros_rest_day(self):
        from nutrition import day_macros
        r = day_macros("rest", "maintain", 75, 180, 30, "m")
        assert r["target_kcal"] > 1500

    def test_day_macros_female(self):
        from nutrition import day_macros
        r = day_macros("endurance", "lose", 60, 165, 28, "f")
        assert r["target_kcal"] > 1200
        assert r["protein_g"] > 50

    def test_supplement_doses(self):
        from nutrition import supplement_doses
        supps = supplement_doses(75)
        assert len(supps) >= 3
        keys = [s["key"] for s in supps]
        assert "caffeine" in keys or "iron" in keys

    def test_supplement_doses_light(self):
        from nutrition import supplement_doses
        supps = supplement_doses(55)
        assert all("dose" in s for s in supps)


class TestDiet:
    """Test diet.py — hydration, fueling rules."""

    def test_import(self):
        import diet
        assert hasattr(diet, 'build_daily_diet')

    def test_build_daily_diet(self):
        from diet import build_daily_diet
        assert callable(build_daily_diet)

    def test_food_constants(self):
        from diet import FOODS, AVOID
        assert isinstance(FOODS, dict) or isinstance(FOODS, list)
        assert isinstance(AVOID, dict) or isinstance(AVOID, list)


class TestDietParser:
    """Test diet_parser.py — OCR PDF parsing."""

    def test_has_parse_functions(self):
        import diet_parser
        assert hasattr(diet_parser, 'parse_diet_pdf')


class TestBiaParser:
    """Test bia_parser.py — body composition parsing."""

    def test_parse_bia_text(self):
        from bia_parser import parse_bia_text
        text = "Body Fat: 15.5%\nMuscle Mass: 35.2 kg\nWater: 55.0%"
        result = parse_bia_text(text)
        assert isinstance(result, dict) or hasattr(result, '__iter__')

    def test_bia_reading_fields(self):
        from bia_parser import BIAReading
        r = BIAReading(fat_mass_pct=15.0, muscle_mass_kg=35.0, hydration_pct=55.0)
        assert r.fat_mass_pct == 15.0
        assert r.muscle_mass_kg == 35.0

    def test_bia_reading_defaults(self):
        from bia_parser import BIAReading
        r = BIAReading()
        assert r.date == ""
        assert r.source == "manual"

    def test_bia_reading_to_dict(self):
        from bia_parser import BIAReading
        r = BIAReading(fat_mass_pct=12.5)
        d = r.to_dict()
        assert isinstance(d, dict)
        assert d["fat_mass_pct"] == 12.5

    def test_parse_bia_pdf_no_file(self):
        from bia_parser import parse_bia_pdf
        result = parse_bia_pdf("/nonexistent/file.pdf")
        assert result is None or isinstance(result, dict)


class TestBiaVision:
    """Test bia_vision.py — BIA image analysis."""

    def test_import(self):
        import bia_vision
        assert hasattr(bia_vision, 'extract_bia_via_vision')

    def test_vision_configured(self):
        from bia_vision import vision_configured
        assert callable(vision_configured)


class TestMetabolicDecoder:
    """Test metabolic_decoder.py — metabolic profiling."""

    def test_import(self):
        import metabolic_decoder
        assert hasattr(metabolic_decoder, 'MetabolicProfile')
