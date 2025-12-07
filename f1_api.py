"""
F1 API service layer for OpenF1 historical data.
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

BASE_URL = "https://api.openf1.org/v1"
TIMEOUT = 10


class F1API:
    """OpenF1 API client for historical Formula 1 data."""

    @staticmethod
    def get_meetings(year: Optional[int] = None, country_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch meetings (races/weekends) filtered by year and/or country."""
        params = {}
        if year:
            params["year"] = year
        if country_name:
            params["country_name"] = country_name
        
        try:
            resp = requests.get(f"{BASE_URL}/meetings", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching meetings: {e}")
            return []

    @staticmethod
    def get_sessions(meeting_key: Optional[int] = None, year: Optional[int] = None, 
                     session_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch sessions (practice, qualifying, race) filtered by meeting or year."""
        params = {}
        if meeting_key:
            params["meeting_key"] = meeting_key
        if year:
            params["year"] = year
        if session_name:
            params["session_name"] = session_name
        
        try:
            resp = requests.get(f"{BASE_URL}/sessions", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching sessions: {e}")
            return []

    @staticmethod
    def get_drivers(session_key: int) -> List[Dict[str, Any]]:
        """Fetch drivers for a given session."""
        params = {"session_key": session_key}
        try:
            resp = requests.get(f"{BASE_URL}/drivers", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching drivers: {e}")
            return []

    @staticmethod
    def get_car_data(session_key: int, driver_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch car telemetry data (speed, RPM, brake, throttle, gear) for a session or driver."""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        
        try:
            resp = requests.get(f"{BASE_URL}/car_data", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching car data: {e}")
            return []

    @staticmethod
    def get_laps(session_key: int, driver_number: Optional[int] = None, 
                 lap_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch lap data (times, sectors, tire data)."""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        if lap_number:
            params["lap_number"] = lap_number
        
        try:
            resp = requests.get(f"{BASE_URL}/laps", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching laps: {e}")
            return []

    @staticmethod
    def get_pit_data(session_key: int, driver_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch pit stop data."""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        
        try:
            resp = requests.get(f"{BASE_URL}/pit", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching pit data: {e}")
            return []

    @staticmethod
    def get_position_data(session_key: int, driver_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch driver position changes over time."""
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        
        try:
            resp = requests.get(f"{BASE_URL}/position", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching position data: {e}")
            return []

    @staticmethod
    def get_weather(session_key: int) -> List[Dict[str, Any]]:
        """Fetch weather data for a session."""
        params = {"session_key": session_key}
        try:
            resp = requests.get(f"{BASE_URL}/weather", params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Error fetching weather: {e}")
            return []

    @staticmethod
    def process_car_data_for_charts(car_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw car data into chart-friendly format."""
        if not car_data:
            return {}
        
        # Sample every Nth point to avoid too many data points (3.7 Hz ~ 1 point per second)
        sample_rate = max(1, len(car_data) // 200)  # Cap at 200 points
        sampled = car_data[::sample_rate]
        
        speeds = [d.get("speed", 0) for d in sampled]
        rpms = [d.get("rpm", 0) for d in sampled]
        throttles = [d.get("throttle", 0) for d in sampled]
        brakes = [d.get("brake", 0) for d in sampled]
        gears = [d.get("n_gear", 0) for d in sampled]
        timestamps = [d.get("date", "").split("T")[1][:8] if d.get("date") else "" for d in sampled]
        
        return {
            "timestamps": timestamps,
            "speeds": speeds,
            "rpms": rpms,
            "throttles": throttles,
            "brakes": brakes,
            "gears": gears,
        }

    @staticmethod
    def process_lap_data_for_charts(lap_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process lap data into chart-friendly format."""
        if not lap_data:
            return {}
        
        lap_numbers = [d.get("lap_number", 0) for d in lap_data]
        lap_durations = [d.get("lap_duration", 0) for d in lap_data]
        sector_1 = [d.get("duration_sector_1", 0) for d in lap_data]
        sector_2 = [d.get("duration_sector_2", 0) for d in lap_data]
        sector_3 = [d.get("duration_sector_3", 0) for d in lap_data]
        i1_speeds = [d.get("i1_speed", 0) for d in lap_data]
        i2_speeds = [d.get("i2_speed", 0) for d in lap_data]
        st_speeds = [d.get("st_speed", 0) for d in lap_data]
        
        return {
            "lap_numbers": lap_numbers,
            "lap_durations": lap_durations,
            "sector_1": sector_1,
            "sector_2": sector_2,
            "sector_3": sector_3,
            "i1_speeds": i1_speeds,
            "i2_speeds": i2_speeds,
            "st_speeds": st_speeds,
        }

    @staticmethod
    def process_position_data_for_charts(position_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process position changes into chart-friendly format."""
        if not position_data:
            return {}
        
        dates = [d.get("date", "").split("T")[1][:8] if d.get("date") else "" for d in position_data]
        positions = [d.get("position", 0) for d in position_data]
        
        return {
            "timestamps": dates,
            "positions": positions,
        }

    @staticmethod
    def process_sector_data(lap_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process sector-by-sector performance data."""
        if not lap_data:
            return {}
        
        lap_numbers = [d.get("lap_number", 0) for d in lap_data]
        sector_1 = [d.get("duration_sector_1", 0) for d in lap_data]
        sector_2 = [d.get("duration_sector_2", 0) for d in lap_data]
        sector_3 = [d.get("duration_sector_3", 0) for d in lap_data]
        
        return {
            "lap_numbers": lap_numbers,
            "sector_1": sector_1,
            "sector_2": sector_2,
            "sector_3": sector_3,
            "total_sector_time": [s1 + s2 + s3 for s1, s2, s3 in zip(sector_1, sector_2, sector_3)]
        }

    @staticmethod
    def compare_drivers(session_key: int, driver_1: int, driver_2: int) -> Dict[str, Any]:
        """Fetch and compare telemetry between two drivers in a session."""
        car_data_1 = F1API.get_car_data(session_key, driver_1)
        car_data_2 = F1API.get_car_data(session_key, driver_2)
        lap_data_1 = F1API.get_laps(session_key, driver_1)
        lap_data_2 = F1API.get_laps(session_key, driver_2)
        
        return {
            "driver_1": {
                "number": driver_1,
                "car_data": F1API.process_car_data_for_charts(car_data_1),
                "lap_data": F1API.process_lap_data_for_charts(lap_data_1),
                "sector_data": F1API.process_sector_data(lap_data_1)
            },
            "driver_2": {
                "number": driver_2,
                "car_data": F1API.process_car_data_for_charts(car_data_2),
                "lap_data": F1API.process_lap_data_for_charts(lap_data_2),
                "sector_data": F1API.process_sector_data(lap_data_2)
            }
        }
