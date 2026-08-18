"""GPX Parser for Cycling Performance Studio Lab.

Parses GPX (GPS Exchange Format) files to extract cycling route data:
- Track points with lat/lon/elevation/time
- Route summaries (distance, elevation gain/loss, duration)
- Power data if present (from Garmin/Cycling computers)

Uses Python's built-in xml.etree.ElementTree for zero external dependencies.
"""

from __future__ import annotations

import logging
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GPX_NS = "http://www.topografix.com/GPX/1/1"
GARMIN_NS = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"


@dataclass
class TrackPoint:
    lat: float
    lon: float
    ele: Optional[float] = None
    time: Optional[datetime] = None
    power: Optional[float] = None
    heart_rate: Optional[int] = None
    cadence: Optional[int] = None
    speed: Optional[float] = None


@dataclass
class TrackSegment:
    points: List[TrackPoint] = field(default_factory=list)

    @property
    def start_time(self) -> Optional[datetime]:
        for p in self.points:
            if p.time:
                return p.time
        return None

    @property
    def end_time(self) -> Optional[datetime]:
        for p in reversed(self.points):
            if p.time:
                return p.time
        return None

    @property
    def duration_seconds(self) -> Optional[float]:
        start = self.start_time
        end = self.end_time
        if start and end:
            return (end - start).total_seconds()
        return None

    @property
    def distance_meters(self) -> float:
        total = 0.0
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            total += _haversine(p1.lat, p1.lon, p2.lat, p2.lon)
        return total

    @property
    def elevation_gain(self) -> float:
        gain = 0.0
        for i in range(1, len(self.points)):
            e1 = self.points[i - 1].ele
            e2 = self.points[i].ele
            if e1 is not None and e2 is not None and e2 > e1:
                gain += e2 - e1
        return gain

    @property
    def elevation_loss(self) -> float:
        loss = 0.0
        for i in range(1, len(self.points)):
            e1 = self.points[i - 1].ele
            e2 = self.points[i].ele
            if e1 is not None and e2 is not None and e2 < e1:
                loss += e1 - e2
        return loss

    @property
    def avg_power(self) -> Optional[float]:
        powers = [p.power for p in self.points if p.power is not None]
        if powers:
            return sum(powers) / len(powers)
        return None

    @property
    def max_power(self) -> Optional[float]:
        powers = [p.power for p in self.points if p.power is not None]
        if powers:
            return max(powers)
        return None

    @property
    def avg_heart_rate(self) -> Optional[int]:
        hrs = [p.heart_rate for p in self.points if p.heart_rate is not None]
        if hrs:
            return int(sum(hrs) / len(hrs))
        return None

    @property
    def max_heart_rate(self) -> Optional[int]:
        hrs = [p.heart_rate for p in self.points if p.heart_rate is not None]
        if hrs:
            return max(hrs)
        return None

    @property
    def avg_speed(self) -> Optional[float]:
        speeds = [p.speed for p in self.points if p.speed is not None]
        if speeds:
            return sum(speeds) / len(speeds)
        dur = self.duration_seconds
        dist = self.distance_meters
        if dur and dur > 0:
            return dist / dur
        return None


@dataclass
class GPXTrack:
    name: Optional[str] = None
    type: Optional[str] = None
    segments: List[TrackSegment] = field(default_factory=list)

    @property
    def total_points(self) -> int:
        return sum(len(s.points) for s in self.segments)

    @property
    def total_distance(self) -> float:
        return sum(s.distance_meters for s in self.segments)

    @property
    def total_elevation_gain(self) -> float:
        return sum(s.elevation_gain for s in self.segments)

    @property
    def total_elevation_loss(self) -> float:
        return sum(s.elevation_loss for s in self.segments)

    @property
    def total_duration(self) -> Optional[float]:
        durations = [s.duration_seconds for s in self.segments if s.duration_seconds]
        if durations:
            return sum(durations)
        return None

    @property
    def start_time(self) -> Optional[datetime]:
        for s in self.segments:
            t = s.start_time
            if t:
                return t
        return None

    @property
    def avg_power(self) -> Optional[float]:
        all_powers = []
        for s in self.segments:
            for p in s.points:
                if p.power is not None:
                    all_powers.append(p.power)
        if all_powers:
            return sum(all_powers) / len(all_powers)
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "total_points": self.total_points,
            "total_distance_m": round(self.total_distance, 1),
            "total_distance_km": round(self.total_distance / 1000, 2),
            "total_elevation_gain_m": round(self.total_elevation_gain, 1),
            "total_elevation_loss_m": round(self.total_elevation_loss, 1),
            "total_duration_s": self.total_duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "avg_power_w": round(self.avg_power, 1) if self.avg_power else None,
        }


@dataclass
class GPXData:
    tracks: List[GPXTrack] = field(default_factory=list)
    filename: str = ""
    creator: str = ""
    version: str = "1.1"

    @property
    def total_tracks(self) -> int:
        return len(self.tracks)

    @property
    def total_distance(self) -> float:
        return sum(t.total_distance for t in self.tracks)

    @property
    def total_elevation_gain(self) -> float:
        return sum(t.total_elevation_gain for t in self.tracks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "creator": self.creator,
            "version": self.version,
            "total_tracks": self.total_tracks,
            "total_distance_km": round(self.total_distance / 1000, 2),
            "total_elevation_gain_m": round(self.total_elevation_gain, 1),
            "tracks": [t.to_dict() for t in self.tracks],
        }


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _parse_time(time_str: str) -> Optional[datetime]:
    if not time_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _parse_float(text: str) -> Optional[float]:
    if text is None:
        return None
    try:
        return float(text.strip())
    except (ValueError, TypeError):
        return None


def _parse_int(text: str) -> Optional[int]:
    if text is None:
        return None
    try:
        return int(float(text.strip()))
    except (ValueError, TypeError):
        return None


def _find_text(element: ET.Element, tag: str, namespace: str = GPX_NS) -> Optional[str]:
    el = element.find(f"{{{namespace}}}{tag}")
    if el is None:
        el = element.find(tag)
    if el is not None and el.text:
        return el.text.strip()
    return None


def _parse_track_point(trkpt: ET.Element) -> TrackPoint:
    lat = float(trkpt.get("lat", "0"))
    lon = float(trkpt.get("lon", "0"))
    ele = _parse_float(_find_text(trkpt, "ele"))
    time_str = _find_text(trkpt, "time")
    time = _parse_time(time_str) if time_str else None

    power = None
    heart_rate = None
    cadence = None
    speed = None

    extensions = trkpt.find(f"{{{GPX_NS}}}extensions")
    if extensions is None:
        extensions = trkpt.find("extensions")

    if extensions is not None:
        for ns in [GARMIN_NS, GPX_NS, ""]:
            prefix = f"{{{ns}}}" if ns else ""
            for el in extensions.iter():
                tag = el.tag.replace(f"{{{ns}}}", "") if ns in el.tag else el.tag
                if tag == "power" and el.text:
                    power = _parse_float(el.text)
                elif tag == "hr" and el.text:
                    heart_rate = _parse_int(el.text)
                elif tag == "cad" and el.text:
                    cadence = _parse_int(el.text)
                elif tag == "speed" and el.text:
                    speed = _parse_float(el.text)

    return TrackPoint(
        lat=lat,
        lon=lon,
        ele=ele,
        time=time,
        power=power,
        heart_rate=heart_rate,
        cadence=cadence,
        speed=speed,
    )


def _parse_track(trk: ET.Element) -> GPXTrack:
    name = _find_text(trk, "name")
    track_type = _find_text(trk, "type")
    segments = []

    for trkseg in trk.findall(f"{{{GPX_NS}}}trkseg"):
        if trkseg is None:
            trkseg = trk.find("trkseg")
        if trkseg is not None:
            points = []
            for trkpt in trkseg.findall(f"{{{GPX_NS}}}trkpt"):
                if trkpt is None:
                    trkpt_pts = trkseg.findall("trkpt")
                else:
                    trkpt_pts = [trkpt]
                for pt in trkpt_pts:
                    points.append(_parse_track_point(pt))
            segments.append(TrackSegment(points=points))

    return GPXTrack(name=name, type=track_type, segments=segments)


def parse_gpx(file_path: str) -> GPXData:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"GPX file not found: {file_path}")

    tree = ET.parse(path)
    root = tree.getroot()

    creator = root.get("creator", "")
    version = root.get("version", "1.1")

    data = GPXData(filename=path.name, creator=creator, version=version)

    for trk in root.findall(f"{{{GPX_NS}}}trk"):
        if trk is None:
            trk_list = root.findall("trk")
        else:
            trk_list = [trk]
        for t in trk_list:
            data.tracks.append(_parse_track(t))

    logger.info(f"Parsed GPX: {path.name} - {data.total_tracks} tracks, {data.total_distance/1000:.1f}km")
    return data


def parse_gpx_string(gpx_content: str) -> GPXData:
    root = ET.fromstring(gpx_content)
    creator = root.get("creator", "")
    version = root.get("version", "1.1")

    data = GPXData(filename="<string>", creator=creator, version=version)

    for trk in root.findall(f"{{{GPX_NS}}}trk"):
        if trk is None:
            trk_list = root.findall("trk")
        else:
            trk_list = [trk]
        for t in trk_list:
            data.tracks.append(_parse_track(t))

    return data


def gpx_to_route_entries(gpx_data: GPXData, profile_id: str) -> List[Dict[str, Any]]:
    entries = []
    for track in gpx_data.tracks:
        for seg_idx, segment in enumerate(track.segments):
            if not segment.points:
                continue
            entry = {
                "source": "gpx_import",
                "filename": gpx_data.filename,
                "track_name": track.name or f"Track {seg_idx + 1}",
                "track_type": track.type,
                "start_time": segment.start_time.isoformat() if segment.start_time else None,
                "duration_seconds": segment.duration_seconds,
                "distance_meters": round(segment.distance_meters, 1),
                "elevation_gain_m": round(segment.elevation_gain, 1),
                "elevation_loss_m": round(segment.elevation_loss, 1),
                "avg_power_w": round(segment.avg_power, 1) if segment.avg_power else None,
                "max_power_w": round(segment.max_power, 1) if segment.max_power else None,
                "avg_hr": segment.avg_heart_rate,
                "max_hr": segment.max_heart_rate,
                "avg_speed_ms": round(segment.avg_speed, 2) if segment.avg_speed else None,
                "point_count": len(segment.points),
                "profile_id": profile_id,
            }
            entries.append(entry)
    return entries


def register_routes(app: Any) -> None:
    from fastapi import Request, UploadFile, File
    from fastapi.responses import JSONResponse

    @app.post("/api/gpx/import")
    async def api_import_gpx(file: UploadFile = File(...)):
        if not file.filename or not file.filename.lower().endswith(".gpx"):
            return JSONResponse({"error": "File must be a .gpx file"}, status_code=400)

        content = await file.read()
        try:
            gpx_text = content.decode("utf-8")
            gpx_data = parse_gpx_string(gpx_text)
            gpx_data.filename = file.filename

            from profile_manager import get as pm_get
            pm = pm_get()
            entries = gpx_to_route_entries(gpx_data, pm.active_id or "default")

            return {
                "success": True,
                "filename": file.filename,
                "summary": gpx_data.to_dict(),
                "routes": entries,
            }
        except ET.ParseError as e:
            return JSONResponse({"error": f"Invalid GPX XML: {str(e)}"}, status_code=400)
        except Exception as e:
            logger.error(f"GPX import failed: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.post("/api/gpx/parse-file")
    async def api_parse_gpx_file(request: Request):
        data = await request.json()
        file_path = data.get("file_path", "")
        if not file_path:
            return JSONResponse({"error": "file_path required"}, status_code=400)

        try:
            gpx_data = parse_gpx(file_path)
            from profile_manager import get as pm_get
            pm = pm_get()
            entries = gpx_to_route_entries(gpx_data, pm.active_id or "default")

            return {
                "success": True,
                "summary": gpx_data.to_dict(),
                "routes": entries,
            }
        except FileNotFoundError as e:
            return JSONResponse({"error": str(e)}, status_code=404)
        except Exception as e:
            logger.error(f"GPX file parse failed: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)
