"""BIA Parser for Cycling Performance Studio Lab.

Parser per file PDF referti BIA (Bioelectrical Impedance Analysis).
Supporto doppio modalità:
1. Vision API esterna (B2B third-party service)
2. Parser locale basato su keyword/Pattern matching (fallback gratuito)
"""

from __future__ import annotations

import asyncio
import re
import logging
from typing import Any, Dict, List, Optional

from config import config
from error_codes import _log_error, REGISTRY

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Flag per attivare/disattivare la Vision API
ENABLE_BIA_VISION = config.BIA_VISION_API_KEY is not None and bool(
    config.BIA_VISION_API_KEY.strip()
)

# Pattern keyword per parser locale (ricerca di valori chiave nei PDF)
LOCAL_PATTERNS: Dict[str, List[str]] = {
    "fat_mass_percentage": [
        r"[Ff]at mass[\s%]+([\d.,]+)",
        r"[Mm]assa grassa[\s%]+([\d.,]+)",
        r"[Bb]ody fat[\s%]+([\d.,]+)",
    ],
    "fat_free_mass": [
        r"[Ff]at free mass[\s]+([\d.,]+)",
        r"[Mm]assa magra[\s]+([\d.,]+)",
        r"[Ll]ean mass[\s]+([\d.,]+)",
    ],
    "body_water_percentage": [
        r"[Aa]ccqua corporea[\s%]+([\d.,]+)",
        r"[Ww]ater[\s%]+([\d.,]+)",
    ],
    "muscle_mass": [
        r"[Mm]uscolo[\s%]+([\d.,]+)",
        r"[Mm]uscle mass[\s%]+([\d.,]+)",
        r"[Mm]uscoli[\s]+([\d.,]+)",
    ],
    "hydration_percentage": [
        r"[Ii]dratazione[\s%]+([\d.,]+)",
        r"[Hh]ydration[\s%]+([\d.,]+)",
    ],
    "protein_mass": [
        r"[Pp]roteine[\s%]+([\d.,]+)",
        r"[Pp]roteic mass[\s%]+([\d.,]+)",
    ],
    "basal_metabolism": [
        r"[Mm]etabolismo basale[\s]+([\d.,]+)",
        r"[Rr]esting metabolic rate[\s]+([\d.,]+)",
    ],
}


# ---------------------------------------------------------------------------
# BIA Vision API Client (optional)
# ---------------------------------------------------------------------------

class BIAVisionClient:
    """Client per BIA Vision API (third-party service)."""

    def __init__(self) -> None:
        self.api_key: str = config.BIA_VISION_API_KEY or ""
        self.base_url: str = config.BIA_VISION_BASE_URL or "https://api.bia.vision/v1"
        self.model: str = config.BIA_VISION_MODEL or "general"

    def is_configured(self) -> bool:
        """Check if Vision API is configured."""
        return ENABLE_BIA_VISION and bool(self.api_key)

    async def analyze_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """Analizza un file PDF usando la Vision API."""
        if not self.is_configured():
            raise ValueError("BIA Vision API non configurata")

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/analyze",
                    headers={"Authorization": f"Bearer {self.api_key}",
                             "Content-Type": "application/pdf"},
                    content=pdf_content,
                    timeout=60.0,
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise ValueError(
                        f"Vision API errore {response.status_code}: {response.text}"
                    )
        except Exception as e:
            _log_error("E_BIA_VISION_FAILED", e)
            raise


# ---------------------------------------------------------------------------
# Local Parser (fallback gratuito)
# ---------------------------------------------------------------------------


def local_pdf_parse(pdf_text: str) -> Optional[Dict[str, Any]]:
    """
    Parser locale di file PDF BIA.

    Estrae metriche chiave usando pattern matching su testo estratto.
    Funziona senza chiave API esterna.
    """
    results: Dict[str, Any] = {}

    for category, patterns in LOCAL_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(",", "."))
                    results[category] = round(value, 1)
                    break
                except ValueError:
                    continue

    # Only return if we found at least one metric
    if results:
        return results
    return None


# ---------------------------------------------------------------------------
# Main BIA Analysis Function
# ---------------------------------------------------------------------------


def analyze_bia(
    pdf_content: bytes,
    pdf_filename: str = "",
    use_vision: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Analisi completa di un file PDF BIA.

    Args:
        pdf_content: Contenuto binario del file PDF
        pdf_filename: Nome file (per logging)
        use_vision: Force the use of Vision API even if not configured

    Returns:
        Dizionario con metriche BIA rilevate
    """
    try:
        # Extract text from PDF (using a external library or fallback)
        pdf_text = _extract_text_from_pdf(pdf_content)

        # Determine mode
        vision_enabled = use_vision or ENABLE_BIA_VISION

        if vision_enabled:
            # Use Vision API
            try:
                import asyncio
                client = BIAVisionClient()
                if client.is_configured():
                    result = asyncio.run(client.analyze_pdf(pdf_content))
                    return _format_results(result)
            except Exception:
                pass  # Fall through to local parser

        # Fallback: local parser
        if not pdf_text:
            return {"error": "Impossibile estrarre testo dal PDF"}

        result = local_pdf_parse(pdf_text)
        if result:
            return result

        # No metrics found
        return {
            "error": "Nessuna metrica BIA riconoscibile trovata nel PDF",
            "suggestion": "Verificare il formato del file PDF o caricare chiave BIA Vision API",
        }

    except Exception as e:
        logger.error(f"BIA analysis failed: {e}")
        return {"error": f"Analisi BIA fallita: {str(e)}"}


def _extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Estrae testo da un file PDF.

    In una implementazione completa, userebbe PyPDF2, pdfminer.six, o similar.
    Per ora restituiamo stringa vuota per simulare il fallback.
    """
    # TODO: Implementare con PyPDF2, pdfminer.six, o similar
    return ""


def _format_results(vision_result: Dict[str, Any]) -> Dict[str, Any]:
    """Formatta i risultati della Vision API in formato standard."""
    formatted: Dict[str, Any] = {}

    # Mappa campi Vision -> formato interno
    field_map: Dict[str, str] = {
        "fat_mass_percentage": "fat_mass_percentage",
        "fat_free_mass": "fat_free_mass",
        "body_water_percentage": "body_water_percentage",
        "muscle_mass": "muscle_mass",
        "hydration_percentage": "hydration_percentage",
        "protein_mass": "protein_mass",
        "basal_metabolism": "basal_metabolism",
    }

    for vision_key, internal_key in field_map.items():
        if vision_key in vision_result:
            try:
                formatted[internal_key] = float(vision_result[vision_key])
            except (ValueError, TypeError):
                formatted[internal_key] = vision_result[vision_key]

    return formatted if formatted else {"error": "Nessun campo riconoscibile dalla Vision API"}