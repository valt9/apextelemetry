"""
F1 API Service Module

Provides integration with the Ergast F1 API for fetching historical race data,
driver information, and generating realistic telemetry data.

The service includes caching mechanisms and fallback data for offline scenarios.

Author: Apex Telemetry Team
Version: 1.0.0
"""

import requests
from datetime import datetime, timedelta
import random as random_module
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class F1APIService:
    """
    Service for fetching F1 data from Ergast F1 API.
    
    Pulls historical data from all past races (2000-present) and includes
    comprehensive driver information with caching for performance.
    
    Attributes:
        BASE_URL (str): Base URL for Ergast F1 API
        drivers_cache (list): Cached list of drivers
        races_cache (dict): Cached race data by year
        driver_races_cache (dict): Cached races per driver
    """
    
    BASE_URL = "https://ergast.com/api/f1"
    
    def __init__(self):
        """Initialize the F1 API service with empty caches."""
        self.drivers_cache = []
        self.races_cache = {}
        self.driver_races_cache = {}
        logger.info("F1 API Service initialized")
    
    def get_drivers(self, year=None):
        """
        Get list of F1 drivers from 2000 to present (modern era).
        
        Fetches drivers from Ergast API with fallback to hardcoded list
        if API is unavailable. Results are cached for performance.
        
        Args:
            year (int, optional): Specific year to fetch drivers from.
                                 If None, fetches all drivers from 2000-present.
        
        Returns:
            list: List of driver dictionaries containing:
                - id (str): Driver ID
                - name (str): Full driver name
                - code (str): 3-letter driver code
                - nationality (str): Driver nationality
                - dateOfBirth (str): Birth date if available
        """
        try:
            drivers_dict = OrderedDict()
            current_year = datetime.now().year
            
            # Test API availability first
            api_available = self._check_api_availability()
            
            if api_available:
                # Fetch drivers from each year from 2000 to current year
                for year in range(2000, current_year + 1):
                    try:
                        url = f"{self.BASE_URL}/{year}/drivers.json?limit=100"
                        response = requests.get(url, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            drivers_list = data.get('MRData', {}).get('DriverTable', {}).get('Drivers', [])
                            
                            # Process unique drivers
                            for driver in drivers_list:
                                driver_id = driver.get('driverId')
                                driver_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip()
                                
                                if driver_id and driver_id not in drivers_dict:
                                    drivers_dict[driver_id] = {
                                        'id': driver_id,
                                        'name': driver_name,
                                        'code': driver.get('code', ''),
                                        'nationality': driver.get('nationality', ''),
                                        'dateOfBirth': driver.get('dateOfBirth', '')
                                    }
                    except requests.RequestException as e:
                        logger.debug(f"Failed to fetch drivers for year {year}: {e}")
                        continue
                    
                if drivers_dict:
                    # Convert to sorted list
                    drivers = sorted(drivers_dict.values(), key=lambda x: x['name'])
                    self.drivers_cache = drivers
                    logger.info(f"Fetched {len(drivers)} unique drivers from API (2000-present)")
                    return drivers
                
        except Exception as e:
            logger.warning(f"Error fetching drivers from API: {e}")
        
        # Return cached drivers if available
        if self.drivers_cache:
            logger.debug("Returning cached drivers")
            return self.drivers_cache
        
        # Fallback to default driver list
        logger.info("Using fallback driver list")
        return self._get_default_drivers()
    
    def _check_api_availability(self):
        """
        Check if Ergast API is available.
        
        Returns:
            bool: True if API is reachable, False otherwise
        """
        try:
            test_url = f"{self.BASE_URL}/2000/drivers.json?limit=1"
            test_response = requests.get(test_url, timeout=5)
            return test_response.status_code == 200
        except requests.RequestException:
            return False
    
    def _get_default_drivers(self):
        """
        Return fallback list of modern F1 drivers (2000-present).
        
        This list is used when the Ergast API is unavailable.
        Includes drivers from 2000s era through current 2024 season.
        
        Returns:
            list: List of driver dictionaries with id, name, code, nationality
        """
        return [
            # Current drivers (2024)
            {'id': 'albon', 'name': 'Alexander Albon', 'code': 'ALB', 'nationality': 'Thai'},
            {'id': 'alonso', 'name': 'Fernando Alonso', 'code': 'ALO', 'nationality': 'Spanish'},
            {'id': 'bearman', 'name': 'Oliver Bearman', 'code': 'BEA', 'nationality': 'British'},
            {'id': 'bottas', 'name': 'Valtteri Bottas', 'code': 'BOT', 'nationality': 'Finnish'},
            {'id': 'gasly', 'name': 'Pierre Gasly', 'code': 'GAS', 'nationality': 'French'},
            {'id': 'hamilton', 'name': 'Lewis Hamilton', 'code': 'HAM', 'nationality': 'British'},
            {'id': 'hulkenberg', 'name': 'Nico Hulkenberg', 'code': 'HUL', 'nationality': 'German'},
            {'id': 'lawson', 'name': 'Liam Lawson', 'code': 'LAW', 'nationality': 'New Zealander'},
            {'id': 'leclerc', 'name': 'Charles Leclerc', 'code': 'LEC', 'nationality': 'Monegasque'},
            {'id': 'magnussen', 'name': 'Kevin Magnussen', 'code': 'MAG', 'nationality': 'Danish'},
            {'id': 'norris', 'name': 'Lando Norris', 'code': 'NOR', 'nationality': 'British'},
            {'id': 'ocon', 'name': 'Esteban Ocon', 'code': 'OCO', 'nationality': 'French'},
            {'id': 'perez', 'name': 'Sergio Perez', 'code': 'PER', 'nationality': 'Mexican'},
            {'id': 'piastri', 'name': 'Oscar Piastri', 'code': 'PIA', 'nationality': 'Australian'},
            {'id': 'ricciardo', 'name': 'Daniel Ricciardo', 'code': 'RIC', 'nationality': 'Australian'},
            {'id': 'russell', 'name': 'George Russell', 'code': 'RUS', 'nationality': 'British'},
            {'id': 'sainz', 'name': 'Carlos Sainz', 'code': 'SAI', 'nationality': 'Spanish'},
            {'id': 'stroll', 'name': 'Lance Stroll', 'code': 'STR', 'nationality': 'Canadian'},
            {'id': 'tsunoda', 'name': 'Yuki Tsunoda', 'code': 'TSU', 'nationality': 'Japanese'},
            {'id': 'verstappen', 'name': 'Max Verstappen', 'code': 'VER', 'nationality': 'Dutch'},
            {'id': 'zhou', 'name': 'Guanyu Zhou', 'code': 'ZHO', 'nationality': 'Chinese'},
            # Recent champions and notable drivers (2010-2023)
            {'id': 'vettel', 'name': 'Sebastian Vettel', 'code': 'VET', 'nationality': 'German'},
            {'id': 'raikkonen', 'name': 'Kimi Raikkonen', 'code': 'RAI', 'nationality': 'Finnish'},
            {'id': 'button', 'name': 'Jenson Button', 'code': 'BUT', 'nationality': 'British'},
            {'id': 'rosberg', 'name': 'Nico Rosberg', 'code': 'ROS', 'nationality': 'German'},
            {'id': 'massa', 'name': 'Felipe Massa', 'code': 'MAS', 'nationality': 'Brazilian'},
            {'id': 'webber', 'name': 'Mark Webber', 'code': 'WEB', 'nationality': 'Australian'},
            {'id': 'kubica', 'name': 'Robert Kubica', 'code': 'KUB', 'nationality': 'Polish'},
            {'id': 'grosjean', 'name': 'Romain Grosjean', 'code': 'GRO', 'nationality': 'French'},
            # 2000s era legends
            {'id': 'schumacher', 'name': 'Michael Schumacher', 'code': 'MSC', 'nationality': 'German'},
            {'id': 'barrichello', 'name': 'Rubens Barrichello', 'code': 'BAR', 'nationality': 'Brazilian'},
            {'id': 'coulthard', 'name': 'David Coulthard', 'code': 'COU', 'nationality': 'British'},
            {'id': 'hakkinen', 'name': 'Mika Hakkinen', 'code': 'HAK', 'nationality': 'Finnish'},
            {'id': 'montoya', 'name': 'Juan Pablo Montoya', 'code': 'MON', 'nationality': 'Colombian'},
            {'id': 'raikkonen', 'name': 'Kimi Raikkonen', 'code': 'RAI', 'nationality': 'Finnish'},
        ]
    
    def get_races_by_year(self, year):
        """
        Get all races for a specific year.
        
        Args:
            year (int): Year to fetch races for
            
        Returns:
            list: List of race dictionaries from Ergast API
        """
        cache_key = f"races_{year}"
        if cache_key in self.races_cache:
            return self.races_cache[cache_key]
        
        try:
            url = f"{self.BASE_URL}/{year}.json?limit=100"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                self.races_cache[cache_key] = races
                logger.debug(f"Fetched {len(races)} races for year {year}")
                return races
        except requests.RequestException as e:
            logger.error(f"Error fetching races for year {year}: {e}")
        
        return []
    
    def get_available_years(self):
        """
        Get list of all available years with race data.
        
        Returns:
            list: Sorted list of year integers (most recent first)
        """
        try:
            url = f"{self.BASE_URL}/seasons.json?limit=100"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                seasons = data.get('MRData', {}).get('SeasonTable', {}).get('Seasons', [])
                years = [int(season.get('season', 0)) for season in seasons if season.get('season')]
                logger.debug(f"Fetched {len(years)} available years")
                return sorted(years, reverse=True)
        except requests.RequestException as e:
            logger.error(f"Error fetching available years: {e}")
        
        # Fallback: return recent years
        current_year = datetime.now().year
        return list(range(current_year, 1999, -1))  # 2000-present, reversed
    
    def get_races_for_driver(self, driver_name):
        """
        Get all races that a specific driver participated in (2000-present).
        
        Fetches actual race participation data from API when available.
        Falls back to generating consistent sample races for all drivers
        to ensure comparisons work properly.
        
        Args:
            driver_name (str): Full name of the F1 driver
            
        Returns:
            list: List of race dictionaries with year, round, name, date, circuit info
        """
        cache_key = f"driver_races_{driver_name}"
        if cache_key in self.driver_races_cache:
            return self.driver_races_cache[cache_key]
        
        races_list = []
        current_year = datetime.now().year
        
        # Find driver ID
        driver_id = None
        drivers = self.get_drivers()
        for driver in drivers:
            if driver['name'].lower() == driver_name.lower():
                driver_id = driver['id']
                break
        
        if not driver_id:
            logger.warning(f"Driver not found: {driver_name}")
            return []
        
        # Check API availability
        api_available = self._check_api_availability()
        
        if api_available:
            # Fetch actual races for the driver
            for year in range(2000, current_year + 1):
                try:
                    url = f"{self.BASE_URL}/{year}.json?limit=100"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                        
                        # Check driver participation in each race
                        for race in races:
                            round_num = race.get('round')
                            race_name = race.get('raceName', '')
                            race_date = race.get('date', '')
                            
                            # Verify driver results for this race
                            try:
                                results_url = f"{self.BASE_URL}/{year}/{round_num}/results.json"
                                results_response = requests.get(results_url, timeout=10)
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    results = results_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                                    if results:
                                        race_results = results[0].get('Results', [])
                                        for result in race_results:
                                            if result.get('Driver', {}).get('driverId') == driver_id:
                                                races_list.append({
                                                    'year': year,
                                                    'round': int(round_num),
                                                    'name': race_name,
                                                    'date': race_date,
                                                    'circuit': race.get('Circuit', {}).get('circuitName', ''),
                                                    'location': race.get('Circuit', {}).get('Location', {}).get('locality', ''),
                                                    'country': race.get('Circuit', {}).get('Location', {}).get('country', ''),
                                                    'display_name': f"{race_name} {year} ({race_date})"
                                                })
                                                break
                            except requests.RequestException:
                                continue
                except requests.RequestException:
                    continue
        
        # If no races found, generate fallback races
        # CRITICAL: Same races for ALL drivers to enable comparisons
        if not races_list:
            races_list = self._generate_fallback_races()
        
        # Sort by date (most recent first)
        races_list.sort(key=lambda x: (x['year'], x['round']), reverse=True)
        self.driver_races_cache[cache_key] = races_list
        logger.debug(f"Found {len(races_list)} races for driver {driver_name}")
        return races_list
    
    def _generate_fallback_races(self):
        """
        Generate consistent fallback races for all drivers.
        
        This ensures all drivers have the same races available for comparison
        when the API is unavailable.
        
        Returns:
            list: List of race dictionaries with consistent dates
        """
        races_list = []
        current_year = datetime.now().year
        
        # Standard F1 calendar circuits
        sample_races = [
            {'name': 'Australian Grand Prix', 'circuit': 'Albert Park Grand Prix Circuit', 'location': 'Melbourne', 'country': 'Australia'},
            {'name': 'Bahrain Grand Prix', 'circuit': 'Bahrain International Circuit', 'location': 'Sakhir', 'country': 'Bahrain'},
            {'name': 'Chinese Grand Prix', 'circuit': 'Shanghai International Circuit', 'location': 'Shanghai', 'country': 'China'},
            {'name': 'Spanish Grand Prix', 'circuit': 'Circuit de Barcelona-Catalunya', 'location': 'Montmeló', 'country': 'Spain'},
            {'name': 'Monaco Grand Prix', 'circuit': 'Circuit de Monaco', 'location': 'Monte-Carlo', 'country': 'Monaco'},
            {'name': 'Canadian Grand Prix', 'circuit': 'Circuit Gilles Villeneuve', 'location': 'Montreal', 'country': 'Canada'},
            {'name': 'British Grand Prix', 'circuit': 'Silverstone Circuit', 'location': 'Silverstone', 'country': 'UK'},
            {'name': 'German Grand Prix', 'circuit': 'Hockenheimring', 'location': 'Hockenheim', 'country': 'Germany'},
            {'name': 'Hungarian Grand Prix', 'circuit': 'Hungaroring', 'location': 'Budapest', 'country': 'Hungary'},
            {'name': 'Belgian Grand Prix', 'circuit': 'Circuit de Spa-Francorchamps', 'location': 'Spa', 'country': 'Belgium'},
            {'name': 'Italian Grand Prix', 'circuit': 'Autodromo Nazionale di Monza', 'location': 'Monza', 'country': 'Italy'},
            {'name': 'Singapore Grand Prix', 'circuit': 'Marina Bay Street Circuit', 'location': 'Marina Bay', 'country': 'Singapore'},
            {'name': 'Japanese Grand Prix', 'circuit': 'Suzuka Circuit', 'location': 'Suzuka', 'country': 'Japan'},
            {'name': 'United States Grand Prix', 'circuit': 'Circuit of the Americas', 'location': 'Austin', 'country': 'USA'},
            {'name': 'Brazilian Grand Prix', 'circuit': 'Autódromo José Carlos Pace', 'location': 'São Paulo', 'country': 'Brazil'},
            {'name': 'Abu Dhabi Grand Prix', 'circuit': 'Yas Marina Circuit', 'location': 'Abu Dhabi', 'country': 'UAE'},
        ]
        
        # Generate races for recent years with consistent dates
        for year in range(max(2020, current_year - 4), current_year + 1):
            for round_num, race_template in enumerate(sample_races[:12], 1):
                # Calculate consistent date: March through October
                base_month = 3
                month = min(10, base_month + ((round_num - 1) // 2))
                day = 15 + ((round_num - 1) % 2) * 7
                
                # Ensure valid day for month
                if month in [4, 6, 9, 11] and day > 30:
                    day = 30
                elif month == 2 and day > 28:
                    day = 28
                    
                race_date = f"{year}-{month:02d}-{day:02d}"
                
                races_list.append({
                    'year': year,
                    'round': round_num,
                    'name': race_template['name'],
                    'date': race_date,
                    'circuit': race_template['circuit'],
                    'location': race_template['location'],
                    'country': race_template['country'],
                    'display_name': f"{race_template['name']} {year} ({race_date})"
                })
        
        return races_list
    
    def get_race_results(self, year, round_num=None, driver_id=None):
        """
        Get race results for a specific year, round, and optionally driver.
        
        Args:
            year (int): Race year
            round_num (int, optional): Specific round number
            driver_id (str, optional): Specific driver ID to filter by
            
        Returns:
            dict or list: Race results data from API
        """
        try:
            if round_num:
                url = f"{self.BASE_URL}/{year}/{round_num}/results.json"
            else:
                url = f"{self.BASE_URL}/{year}/results.json?limit=100"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                
                if driver_id and races:
                    # Filter for specific driver
                    for race in races:
                        results = race.get('Results', [])
                        for result in results:
                            if result.get('Driver', {}).get('driverId') == driver_id:
                                return {
                                    'race': race,
                                    'result': result
                                }
                
                return races
        except requests.RequestException as e:
            logger.error(f"Error fetching race results: {e}")
        
        return None
    
    def fetch_race_data(self, driver_name, race_date=None):
        """
        Fetch race telemetry data for a driver using historical race data.
        
        Uses actual race results when available and enhances with realistic
        simulated telemetry data.
        
        Args:
            driver_name (str): Full name of the F1 driver
            race_date (str, optional): Race date in YYYY-MM-DD format
            
        Returns:
            list: List of telemetry data points with timestamps
        """
        try:
            year = None
            race_results = None
            
            # Parse race date to get year
            if race_date:
                try:
                    date_obj = datetime.strptime(race_date, '%Y-%m-%d')
                    year = date_obj.year
                except ValueError as e:
                    logger.error(f"Invalid date format: {race_date}, {e}")
                    year = datetime.now().year
            else:
                year = datetime.now().year
            
            # Find driver ID
            driver_id = None
            drivers = self.get_drivers()
            for driver in drivers:
                if driver['name'].lower() == driver_name.lower():
                    driver_id = driver['id']
                    break
            
            # Try to fetch actual race results
            if driver_id and year:
                races = self.get_races_by_year(year)
                
                # Find closest race to specified date
                target_date = datetime.strptime(race_date, '%Y-%m-%d') if race_date else datetime.now()
                closest_race = None
                min_date_diff = None
                
                for race in races:
                    try:
                        race_date_str = race.get('date', '')
                        if race_date_str:
                            race_date_obj = datetime.strptime(race_date_str, '%Y-%m-%d')
                            date_diff = abs((target_date - race_date_obj).days)
                            
                            if min_date_diff is None or date_diff < min_date_diff:
                                min_date_diff = date_diff
                                closest_race = race
                    except ValueError:
                        continue
                
                # Get race results for the driver
                if closest_race:
                    round_num = closest_race.get('round')
                    race_results = self.get_race_results(year, round_num, driver_id)
                    logger.debug(f"Found race results for {driver_name} in {year}")
            
            # Generate telemetry data
            return self._generate_enhanced_data(driver_name, race_results, year, race_date)
            
        except Exception as e:
            logger.error(f"Error fetching race data: {e}")
            return self._generate_enhanced_data(driver_name, None, None, race_date)
    
    def _generate_enhanced_data(self, driver_name, race_result, year, race_date):
        """
        Generate telemetry data enhanced with actual race results when available.
        
        Uses driver-specific seeding to generate consistent, realistic data.
        Each driver gets unique but reproducible performance characteristics.
        
        Args:
            driver_name (str): Driver name
            race_result (dict, optional): Actual race results from API
            year (int, optional): Race year
            race_date (str, optional): Race date
            
        Returns:
            list: List of telemetry dictionaries with speed, RPM, lap times, etc.
        """
        data_points = []
        base_time = datetime.now()
        
        # Use actual race date if provided
        if race_date:
            try:
                base_time = datetime.strptime(race_date, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Extract actual race data if available
        actual_position = None
        actual_laps = 50  # Standard race distance
        fastest_lap_time = None
        
        if race_result and isinstance(race_result, dict) and 'result' in race_result:
            result = race_result['result']
            try:
                actual_position = int(result.get('position', 0))
            except (ValueError, TypeError):
                actual_position = None
                
            fastest_lap = result.get('FastestLap', {})
            if fastest_lap:
                fastest_lap_time_str = fastest_lap.get('Time', {}).get('time', '')
                if fastest_lap_time_str:
                    try:
                        # Parse time string like "1:23.456"
                        parts = fastest_lap_time_str.split(':')
                        if len(parts) == 2:
                            minutes, seconds = parts
                            fastest_lap_time = float(minutes) * 60 + float(seconds)
                    except (ValueError, IndexError):
                        pass
        
        # Create driver-specific random number generator
        # This ensures consistent data for each driver while avoiding global state pollution
        driver_hash = hash(driver_name) % 1000
        rng = random_module.Random(driver_hash)
        
        # Driver-specific performance modifiers
        performance_modifier = (driver_hash % 20) - 10
        speed_modifier = performance_modifier * 1.5
        lap_time_modifier = performance_modifier * 0.15
        consistency_modifier = (driver_hash % 5) + 1
        
        # Determine starting position
        if actual_position:
            start_position = actual_position
        else:
            start_position = max(1, min(20, 5 + (performance_modifier // 2)))
        
        # Base lap time calculation
        if fastest_lap_time:
            base_lap_time = fastest_lap_time + 2.0  # Buffer above fastest lap
        else:
            base_lap_time = 85 - lap_time_modifier
        
        # Generate telemetry for each lap
        for lap in range(1, actual_laps + 1):
            # Base values with driver-specific variations
            base_speed = 280 + speed_modifier + rng.uniform(-20, 20)
            base_rpm = 12000 + rng.uniform(-500, 500)
            
            # Tire wear increases progressively
            tire_wear_rate = 1.8 + (consistency_modifier * 0.1)
            tire_wear = min(100, (lap / actual_laps) * 100 * tire_wear_rate + rng.uniform(-5, 5))
            
            # Tire temperature correlates with wear
            tire_temp = 90 + (tire_wear * 0.3) + rng.uniform(-5, 5)
            
            # Lap time degrades with tire wear
            lap_time = base_lap_time + (tire_wear * 0.1) + rng.uniform(-2, 2) / consistency_modifier
            
            # Sector time (approximately 1/3 of lap)
            sector_time = lap_time / 3 + rng.uniform(-0.5, 0.5) / consistency_modifier
            
            # Position changes slightly over race
            if actual_position:
                position = max(1, min(20, actual_position + int(rng.uniform(-1, 1))))
            else:
                position_variation = int(rng.uniform(-3, 3) - (performance_modifier / 3))
                position = max(1, min(20, start_position + position_variation + (lap // 15)))
            
            # Speed reduces as tires wear
            speed = base_speed - (tire_wear * 0.5) + rng.uniform(-10, 10)
            
            # RPM correlates with speed
            rpm = base_rpm + (speed - 280) * 10 + rng.uniform(-200, 200)
            
            timestamp = base_time + timedelta(seconds=lap * lap_time)
            
            data_points.append({
                'speed': round(speed, 2),
                'rpm': round(rpm, 0),
                'lap_time': round(lap_time, 3),
                'tire_temp': round(tire_temp, 1),
                'tire_wear': round(tire_wear, 1),
                'sector_time': round(sector_time, 3),
                'position': position,
                'timestamp': timestamp,
                'lap': lap
            })
        
        logger.info(f"Generated {len(data_points)} telemetry points for {driver_name}")
        return data_points
                                
                                # Store unique drivers
                                if driver_id and driver_id not in drivers_dict:
                                    drivers_dict[driver_id] = {
                                        'id': driver_id,
                                        'name': driver_name,
                                        'code': driver.get('code', ''),
                                        'nationality': driver.get('nationality', ''),
                                        'dateOfBirth': driver.get('dateOfBirth', '')
                                    }
                    except Exception:
                        # Silently continue if API call fails for a specific year
                        continue
                    
                if drivers_dict:
                    # Convert to list and sort by name
                    drivers = sorted(drivers_dict.values(), key=lambda x: x['name'])
                    self.drivers_cache = drivers
                    print(f"Fetched {len(drivers)} unique drivers from 2000-present via API")
                    return drivers
                
        except Exception as e:
            # Only log if it's not a connection error (expected when offline)
            if "Connection" not in str(type(e).__name__):
                print(f"Error fetching drivers from API: {e}")
        
        # Fallback to cached drivers
        if self.drivers_cache:
            return self.drivers_cache
        
        # Fallback list with modern drivers (2000-present)
        return self._get_default_drivers()
    
    def _get_default_drivers(self):
        """Return list of modern F1 drivers (2000-present)"""
        return [
            # Current drivers (2024)
            {'id': 'albon', 'name': 'Alexander Albon', 'code': 'ALB', 'nationality': 'Thai'},
            {'id': 'alonso', 'name': 'Fernando Alonso', 'code': 'ALO', 'nationality': 'Spanish'},
            {'id': 'bearman', 'name': 'Oliver Bearman', 'code': 'BEA', 'nationality': 'British'},
            {'id': 'bottas', 'name': 'Valtteri Bottas', 'code': 'BOT', 'nationality': 'Finnish'},
            {'id': 'gasly', 'name': 'Pierre Gasly', 'code': 'GAS', 'nationality': 'French'},
            {'id': 'hamilton', 'name': 'Lewis Hamilton', 'code': 'HAM', 'nationality': 'British'},
            {'id': 'hulkenberg', 'name': 'Nico Hulkenberg', 'code': 'HUL', 'nationality': 'German'},
            {'id': 'lawson', 'name': 'Liam Lawson', 'code': 'LAW', 'nationality': 'New Zealander'},
            {'id': 'leclerc', 'name': 'Charles Leclerc', 'code': 'LEC', 'nationality': 'Monegasque'},
            {'id': 'magnussen', 'name': 'Kevin Magnussen', 'code': 'MAG', 'nationality': 'Danish'},
            {'id': 'norris', 'name': 'Lando Norris', 'code': 'NOR', 'nationality': 'British'},
            {'id': 'ocon', 'name': 'Esteban Ocon', 'code': 'OCO', 'nationality': 'French'},
            {'id': 'perez', 'name': 'Sergio Perez', 'code': 'PER', 'nationality': 'Mexican'},
            {'id': 'piastri', 'name': 'Oscar Piastri', 'code': 'PIA', 'nationality': 'Australian'},
            {'id': 'ricciardo', 'name': 'Daniel Ricciardo', 'code': 'RIC', 'nationality': 'Australian'},
            {'id': 'russell', 'name': 'George Russell', 'code': 'RUS', 'nationality': 'British'},
            {'id': 'sainz', 'name': 'Carlos Sainz', 'code': 'SAI', 'nationality': 'Spanish'},
            {'id': 'stroll', 'name': 'Lance Stroll', 'code': 'STR', 'nationality': 'Canadian'},
            {'id': 'tsunoda', 'name': 'Yuki Tsunoda', 'code': 'TSU', 'nationality': 'Japanese'},
            {'id': 'verstappen', 'name': 'Max Verstappen', 'code': 'VER', 'nationality': 'Dutch'},
            {'id': 'zhou', 'name': 'Guanyu Zhou', 'code': 'ZHO', 'nationality': 'Chinese'},
            # Recent drivers (2010-2023)
            {'id': 'vettel', 'name': 'Sebastian Vettel', 'code': 'VET', 'nationality': 'German'},
            {'id': 'raikkonen', 'name': 'Kimi Raikkonen', 'code': 'RAI', 'nationality': 'Finnish'},
            {'id': 'button', 'name': 'Jenson Button', 'code': 'BUT', 'nationality': 'British'},
            {'id': 'rosberg', 'name': 'Nico Rosberg', 'code': 'ROS', 'nationality': 'German'},
            {'id': 'massa', 'name': 'Felipe Massa', 'code': 'MAS', 'nationality': 'Brazilian'},
            {'id': 'webber', 'name': 'Mark Webber', 'code': 'WEB', 'nationality': 'Australian'},
            {'id': 'kubica', 'name': 'Robert Kubica', 'code': 'KUB', 'nationality': 'Polish'},
            {'id': 'grosjean', 'name': 'Romain Grosjean', 'code': 'GRO', 'nationality': 'French'},
            {'id': 'kvyat', 'name': 'Daniil Kvyat', 'code': 'KVY', 'nationality': 'Russian'},
            {'id': 'giovinazzi', 'name': 'Antonio Giovinazzi', 'code': 'GIO', 'nationality': 'Italian'},
            {'id': 'latifi', 'name': 'Nicholas Latifi', 'code': 'LAT', 'nationality': 'Canadian'},
            {'id': 'mazepin', 'name': 'Nikita Mazepin', 'code': 'MAZ', 'nationality': 'Russian'},
            {'id': 'mick_schumacher', 'name': 'Mick Schumacher', 'code': 'MSC', 'nationality': 'German'},
            {'id': 'de_vries', 'name': 'Nyck de Vries', 'code': 'DEV', 'nationality': 'Dutch'},
            {'id': 'sargeant', 'name': 'Logan Sargeant', 'code': 'SAR', 'nationality': 'American'},
            # 2000s era drivers
            {'id': 'barrichello', 'name': 'Rubens Barrichello', 'code': 'BAR', 'nationality': 'Brazilian'},
            {'id': 'coulthard', 'name': 'David Coulthard', 'code': 'COU', 'nationality': 'British'},
            {'id': 'hakkinen', 'name': 'Mika Hakkinen', 'code': 'HAK', 'nationality': 'Finnish'},
            {'id': 'montoya', 'name': 'Juan Pablo Montoya', 'code': 'MON', 'nationality': 'Colombian'},
            {'id': 'trulli', 'name': 'Jarno Trulli', 'code': 'TRU', 'nationality': 'Italian'},
            {'id': 'fisichella', 'name': 'Giancarlo Fisichella', 'code': 'FIS', 'nationality': 'Italian'},
            {'id': 'heidfeld', 'name': 'Nick Heidfeld', 'code': 'HEI', 'nationality': 'German'},
            {'id': 'irvine', 'name': 'Eddie Irvine', 'code': 'IRV', 'nationality': 'British'},
            {'id': 'villeneuve', 'name': 'Jacques Villeneuve', 'code': 'VIL', 'nationality': 'Canadian'},
            {'id': 'ralf_schumacher', 'name': 'Ralf Schumacher', 'code': 'RSC', 'nationality': 'German'},
            {'id': 'frentzen', 'name': 'Heinz-Harald Frentzen', 'code': 'FRE', 'nationality': 'German'},
            {'id': 'panis', 'name': 'Olivier Panis', 'code': 'PAN', 'nationality': 'French'},
            {'id': 'herbert', 'name': 'Johnny Herbert', 'code': 'HER', 'nationality': 'British'},
            {'id': 'diniz', 'name': 'Pedro Diniz', 'code': 'DIN', 'nationality': 'Brazilian'},
            {'id': 'wurz', 'name': 'Alexander Wurz', 'code': 'WUR', 'nationality': 'Austrian'},
            {'id': 'salo', 'name': 'Mika Salo', 'code': 'SAL', 'nationality': 'Finnish'},
            {'id': 'gene', 'name': 'Marc Gene', 'code': 'GEN', 'nationality': 'Spanish'},
            {'id': 'zonta', 'name': 'Ricardo Zonta', 'code': 'ZON', 'nationality': 'Brazilian'},
            {'id': 'de_la_rosa', 'name': 'Pedro de la Rosa', 'code': 'DLR', 'nationality': 'Spanish'},
            {'id': 'mazzacane', 'name': 'Gastón Mazzacane', 'code': 'MAZ', 'nationality': 'Argentine'},
            {'id': 'verstappen_jos', 'name': 'Jos Verstappen', 'code': 'VER', 'nationality': 'Dutch'},
            {'id': 'burti', 'name': 'Luciano Burti', 'code': 'BUR', 'nationality': 'Brazilian'},
            {'id': 'bernoldi', 'name': 'Enrique Bernoldi', 'code': 'BER', 'nationality': 'Brazilian'},
            {'id': 'mcnish', 'name': 'Allan McNish', 'code': 'MCN', 'nationality': 'British'},
            {'id': 'yoong', 'name': 'Alex Yoong', 'code': 'YOO', 'nationality': 'Malaysian'},
            {'id': 'sato', 'name': 'Takuma Sato', 'code': 'SAT', 'nationality': 'Japanese'},
            {'id': 'da_matta', 'name': 'Cristiano da Matta', 'code': 'DAM', 'nationality': 'Brazilian'},
            {'id': 'firman', 'name': 'Ralph Firman', 'code': 'FIR', 'nationality': 'British'},
            {'id': 'wilson', 'name': 'Justin Wilson', 'code': 'WIL', 'nationality': 'British'},
            {'id': 'baumgartner', 'name': 'Zsolt Baumgartner', 'code': 'BAU', 'nationality': 'Hungarian'},
            {'id': 'bruni', 'name': 'Gianmaria Bruni', 'code': 'BRU', 'nationality': 'Italian'},
            {'id': 'pantano', 'name': 'Giorgio Pantano', 'code': 'PAN', 'nationality': 'Italian'},
            {'id': 'glock', 'name': 'Timo Glock', 'code': 'GLO', 'nationality': 'German'},
            {'id': 'klien', 'name': 'Christian Klien', 'code': 'KLI', 'nationality': 'Austrian'},
            {'id': 'liuzzi', 'name': 'Vitantonio Liuzzi', 'code': 'LIU', 'nationality': 'Italian'},
            {'id': 'monteiro', 'name': 'Tiago Monteiro', 'code': 'MON', 'nationality': 'Portuguese'},
            {'id': 'karthikeyan', 'name': 'Narain Karthikeyan', 'code': 'KAR', 'nationality': 'Indian'},
            {'id': 'albers', 'name': 'Christijan Albers', 'code': 'ALB', 'nationality': 'Dutch'},
            {'id': 'doornbos', 'name': 'Robert Doornbos', 'code': 'DOO', 'nationality': 'Dutch'},
            {'id': 'yamamoto', 'name': 'Sakon Yamamoto', 'code': 'YAM', 'nationality': 'Japanese'},
            {'id': 'sutil', 'name': 'Adrian Sutil', 'code': 'SUT', 'nationality': 'German'},
            {'id': 'nakajima', 'name': 'Kazuki Nakajima', 'code': 'NAK', 'nationality': 'Japanese'},
            {'id': 'bourdais', 'name': 'Sebastien Bourdais', 'code': 'BOU', 'nationality': 'French'},
            {'id': 'piquet_jr', 'name': 'Nelson Piquet Jr.', 'code': 'PIQ', 'nationality': 'Brazilian'},
            {'id': 'buemi', 'name': 'Sebastien Buemi', 'code': 'BUE', 'nationality': 'Swiss'},
            {'id': 'alguesuari', 'name': 'Jaime Alguersuari', 'code': 'ALG', 'nationality': 'Spanish'},
            {'id': 'badoer', 'name': 'Luca Badoer', 'code': 'BAD', 'nationality': 'Italian'},
            {'id': 'lucas_di_grassi', 'name': 'Lucas di Grassi', 'code': 'DIG', 'nationality': 'Brazilian'},
            {'id': 'chandhok', 'name': 'Karun Chandhok', 'code': 'CHA', 'nationality': 'Indian'},
            {'id': 'bruno_senna', 'name': 'Bruno Senna', 'code': 'SEN', 'nationality': 'Brazilian'},
            {'id': 'petrov', 'name': 'Vitaly Petrov', 'code': 'PET', 'nationality': 'Russian'},
            {'id': 'ambrosio', 'name': 'Jerome d\'Ambrosio', 'code': 'DAM', 'nationality': 'Belgian'},
            {'id': 'chilton', 'name': 'Max Chilton', 'code': 'CHI', 'nationality': 'British'},
            {'id': 'van_der_garde', 'name': 'Giedo van der Garde', 'code': 'VDG', 'nationality': 'Dutch'},
            {'id': 'bianchi', 'name': 'Jules Bianchi', 'code': 'BIA', 'nationality': 'French'},
            {'id': 'gutierrez', 'name': 'Esteban Gutierrez', 'code': 'GUT', 'nationality': 'Mexican'},
            {'id': 'ericsson', 'name': 'Marcus Ericsson', 'code': 'ERI', 'nationality': 'Swedish'},
            {'id': 'stevens', 'name': 'Will Stevens', 'code': 'STE', 'nationality': 'British'},
            {'id': 'merhi', 'name': 'Roberto Merhi', 'code': 'MER', 'nationality': 'Spanish'},
            {'id': 'rossi', 'name': 'Alexander Rossi', 'code': 'ROS', 'nationality': 'American'},
            {'id': 'wehrlein', 'name': 'Pascal Wehrlein', 'code': 'WEH', 'nationality': 'German'},
            {'id': 'haryanto', 'name': 'Rio Haryanto', 'code': 'HAR', 'nationality': 'Indonesian'},
            {'id': 'palmer', 'name': 'Jolyon Palmer', 'code': 'PAL', 'nationality': 'British'},
            {'id': 'vandoorne', 'name': 'Stoffel Vandoorne', 'code': 'VAN', 'nationality': 'Belgian'},
            {'id': 'sirotkin', 'name': 'Sergey Sirotkin', 'code': 'SIR', 'nationality': 'Russian'},
        ]
    
    def get_races_by_year(self, year):
        """Get all races for a specific year"""
        cache_key = f"races_{year}"
        if cache_key in self.races_cache:
            return self.races_cache[cache_key]
        
        try:
            url = f"{self.BASE_URL}/{year}.json?limit=100"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                self.races_cache[cache_key] = races
                return races
        except Exception as e:
            print(f"Error fetching races for year {year}: {e}")
        
        return []
    
    def get_available_years(self):
        """Get list of all available years with race data"""
        try:
            # Get seasons endpoint
            url = f"{self.BASE_URL}/seasons.json?limit=100"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                seasons = data.get('MRData', {}).get('SeasonTable', {}).get('Seasons', [])
                years = [int(season.get('season', 0)) for season in seasons if season.get('season')]
                return sorted(years, reverse=True)  # Most recent first
        except Exception as e:
            print(f"Error fetching available years: {e}")
        
        # Fallback: return recent years
        current_year = datetime.now().year
        return list(range(2000, current_year + 1))
    
    def get_races_for_driver(self, driver_name):
        """Get all races that a specific driver participated in (2000-present)"""
        cache_key = f"driver_races_{driver_name}"
        if cache_key in self.driver_races_cache:
            return self.driver_races_cache[cache_key]
        
        races_list = []
        current_year = datetime.now().year
        
        # Find driver ID
        driver_id = None
        drivers = self.get_drivers()
        for driver in drivers:
            if driver['name'].lower() == driver_name.lower():
                driver_id = driver['id']
                break
        
        if not driver_id:
            return []
        
        # Check if API is available
        api_available = False
        try:
            test_url = f"{self.BASE_URL}/2000/drivers.json?limit=1"
            test_response = requests.get(test_url, timeout=5)
            if test_response.status_code == 200:
                api_available = True
        except:
            pass
        
        if api_available:
            # Fetch races for each year from 2000 to current
            for year in range(2000, current_year + 1):
                try:
                    # Get all races for the year
                    url = f"{self.BASE_URL}/{year}.json?limit=100"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                        
                        # Check if driver participated in each race
                        for race in races:
                            round_num = race.get('round')
                            race_name = race.get('raceName', '')
                            race_date = race.get('date', '')
                            
                            # Check if driver has results in this race
                            try:
                                results_url = f"{self.BASE_URL}/{year}/{round_num}/results.json"
                                results_response = requests.get(results_url, timeout=10)
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    results = results_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                                    if results:
                                        race_results = results[0].get('Results', [])
                                        for result in race_results:
                                            if result.get('Driver', {}).get('driverId') == driver_id:
                                                races_list.append({
                                                    'year': year,
                                                    'round': int(round_num),
                                                    'name': race_name,
                                                    'date': race_date,
                                                    'circuit': race.get('Circuit', {}).get('circuitName', ''),
                                                    'location': race.get('Circuit', {}).get('Location', {}).get('locality', ''),
                                                    'country': race.get('Circuit', {}).get('Location', {}).get('country', ''),
                                                    'display_name': f"{race_name} {year} ({race_date})"
                                                })
                                                break
                            except:
                                continue
                except:
                    continue
        
        # If no races found from API, generate fallback races for ALL drivers
        # This ensures all drivers have the same races available for comparison
        if not races_list:
            # Generate sample races for common F1 circuits (2000-present)
            # IMPORTANT: Same races for all drivers so comparisons work
            current_year = datetime.now().year
            sample_races = [
                {'name': 'Australian Grand Prix', 'circuit': 'Albert Park Grand Prix Circuit', 'location': 'Melbourne', 'country': 'Australia'},
                {'name': 'Bahrain Grand Prix', 'circuit': 'Bahrain International Circuit', 'location': 'Sakhir', 'country': 'Bahrain'},
                {'name': 'Chinese Grand Prix', 'circuit': 'Shanghai International Circuit', 'location': 'Shanghai', 'country': 'China'},
                {'name': 'Spanish Grand Prix', 'circuit': 'Circuit de Barcelona-Catalunya', 'location': 'Montmeló', 'country': 'Spain'},
                {'name': 'Monaco Grand Prix', 'circuit': 'Circuit de Monaco', 'location': 'Monte-Carlo', 'country': 'Monaco'},
                {'name': 'Canadian Grand Prix', 'circuit': 'Circuit Gilles Villeneuve', 'location': 'Montreal', 'country': 'Canada'},
                {'name': 'British Grand Prix', 'circuit': 'Silverstone Circuit', 'location': 'Silverstone', 'country': 'UK'},
                {'name': 'German Grand Prix', 'circuit': 'Hockenheimring', 'location': 'Hockenheim', 'country': 'Germany'},
                {'name': 'Hungarian Grand Prix', 'circuit': 'Hungaroring', 'location': 'Budapest', 'country': 'Hungary'},
                {'name': 'Belgian Grand Prix', 'circuit': 'Circuit de Spa-Francorchamps', 'location': 'Spa', 'country': 'Belgium'},
                {'name': 'Italian Grand Prix', 'circuit': 'Autodromo Nazionale di Monza', 'location': 'Monza', 'country': 'Italy'},
                {'name': 'Singapore Grand Prix', 'circuit': 'Marina Bay Street Circuit', 'location': 'Marina Bay', 'country': 'Singapore'},
                {'name': 'Japanese Grand Prix', 'circuit': 'Suzuka Circuit', 'location': 'Suzuka', 'country': 'Japan'},
                {'name': 'United States Grand Prix', 'circuit': 'Circuit of the Americas', 'location': 'Austin', 'country': 'USA'},
                {'name': 'Brazilian Grand Prix', 'circuit': 'Autódromo José Carlos Pace', 'location': 'São Paulo', 'country': 'Brazil'},
                {'name': 'Abu Dhabi Grand Prix', 'circuit': 'Yas Marina Circuit', 'location': 'Abu Dhabi', 'country': 'UAE'},
            ]
            
            # Generate races for recent years (same for all drivers)
            # Use consistent dates so all drivers have the same races
            for year in range(max(2020, current_year - 4), current_year + 1):
                for round_num, race_template in enumerate(sample_races[:12], 1):  # First 12 races per year
                    # Calculate consistent date based on year and round
                    # March through October, every 2-3 weeks
                    base_month = 3
                    month = min(10, base_month + ((round_num - 1) // 2))
                    day = 15 + ((round_num - 1) % 2) * 7
                    # Ensure valid day for the month
                    if month in [4, 6, 9, 11] and day > 30:
                        day = 30
                    elif month == 2 and day > 28:
                        day = 28
                    race_date = f"{year}-{month:02d}-{day:02d}"
                    races_list.append({
                        'year': year,
                        'round': round_num,
                        'name': race_template['name'],
                        'date': race_date,
                        'circuit': race_template['circuit'],
                        'location': race_template['location'],
                        'country': race_template['country'],
                        'display_name': f"{race_template['name']} {year} ({race_date})"
                    })
        
        # Sort by date (most recent first)
        races_list.sort(key=lambda x: (x['year'], x['round']), reverse=True)
        self.driver_races_cache[cache_key] = races_list
        return races_list
    
    def get_race_results(self, year, round_num=None, driver_id=None):
        """Get race results for a specific year, round, and optionally driver"""
        try:
            if round_num:
                url = f"{self.BASE_URL}/{year}/{round_num}/results.json"
            else:
                url = f"{self.BASE_URL}/{year}/results.json?limit=100"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                races = data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                
                if driver_id and races:
                    # Filter results for specific driver
                    for race in races:
                        results = race.get('Results', [])
                        for result in results:
                            if result.get('Driver', {}).get('driverId') == driver_id:
                                return {
                                    'race': race,
                                    'result': result
                                }
                
                return races
        except Exception as e:
            print(f"Error fetching race results: {e}")
        
        return None
    
    def fetch_race_data(self, driver_name, race_date=None):
        """
        Fetch race telemetry data for a driver using historical race data
        Uses actual race results and enhances with realistic telemetry
        """
        try:
            year = None
            race_results = None
            
            # Parse race date to get year
            if race_date:
                try:
                    date_obj = datetime.strptime(race_date, '%Y-%m-%d')
                    year = date_obj.year
                except:
                    year = datetime.now().year
            else:
                year = datetime.now().year
            
            # Find driver ID from name
            driver_id = None
            drivers = self.get_drivers()
            for driver in drivers:
                if driver['name'].lower() == driver_name.lower():
                    driver_id = driver['id']
                    break
            
            # Try to fetch actual race results
            if driver_id and year:
                # Get all races for the year
                races = self.get_races_by_year(year)
                
                # Find the race closest to the specified date
                target_date = datetime.strptime(race_date, '%Y-%m-%d') if race_date else datetime.now()
                closest_race = None
                min_date_diff = None
                
                for race in races:
                    try:
                        race_date_str = race.get('date', '')
                        if race_date_str:
                            race_date_obj = datetime.strptime(race_date_str, '%Y-%m-%d')
                            date_diff = abs((target_date - race_date_obj).days)
                            
                            if min_date_diff is None or date_diff < min_date_diff:
                                min_date_diff = date_diff
                                closest_race = race
                    except:
                        continue
                
                # Get race results for the driver
                if closest_race:
                    round_num = closest_race.get('round')
                    race_results = self.get_race_results(year, round_num, driver_id)
            
            # Generate telemetry data based on actual race results if available
            return self._generate_enhanced_data(driver_name, race_results, year, race_date)
            
        except Exception as e:
            print(f"Error fetching race data: {e}")
            return self._generate_enhanced_data(driver_name, None, None, race_date)
    
    def _generate_enhanced_data(self, driver_name, race_result, year, race_date):
        """
        Generate telemetry data enhanced with actual race results when available
        """
        data_points = []
        base_time = datetime.now()
        
        # If we have actual race date, use it
        if race_date:
            try:
                base_time = datetime.strptime(race_date, '%Y-%m-%d')
            except:
                pass
        
        # Extract actual race data if available
        actual_position = None
        actual_laps = 50  # Default
        fastest_lap_time = None
        
        if race_result and isinstance(race_result, dict) and 'result' in race_result:
            result = race_result['result']
            actual_position = int(result.get('position', 0))
            fastest_lap = result.get('FastestLap', {})
            if fastest_lap:
                fastest_lap_time_str = fastest_lap.get('Time', {}).get('time', '')
                if fastest_lap_time_str:
                    try:
                        # Parse time string like "1:23.456"
                        parts = fastest_lap_time_str.split(':')
                        if len(parts) == 2:
                            minutes, seconds = parts
                            fastest_lap_time = float(minutes) * 60 + float(seconds)
                    except:
                        pass
        
        # Generate consistent seed based on driver name
        driver_hash = hash(driver_name) % 1000
        random.seed(driver_hash)
        
        # Performance modifiers based on driver
        performance_modifier = (driver_hash % 20) - 10
        speed_modifier = performance_modifier * 1.5
        lap_time_modifier = performance_modifier * 0.15
        consistency_modifier = (driver_hash % 5) + 1
        
        # Use actual position if available, otherwise calculate
        if actual_position:
            start_position = actual_position
        else:
            start_position = max(1, min(20, 5 + (performance_modifier // 2)))
        
        # Base lap time - use fastest lap if available, otherwise calculate
        if fastest_lap_time:
            base_lap_time = fastest_lap_time + 2.0  # Add buffer to fastest lap
        else:
            base_lap_time = 85 - lap_time_modifier
        
        # Generate telemetry for each lap
        for lap in range(1, actual_laps + 1):
            # Base values with driver-specific modifiers
            base_speed = 280 + speed_modifier + random.uniform(-20, 20)
            base_rpm = 12000 + random.uniform(-500, 500)
            
            # Tire wear increases over time
            tire_wear_rate = 1.8 + (consistency_modifier * 0.1)
            tire_wear = min(100, (lap / actual_laps) * 100 * tire_wear_rate + random.uniform(-5, 5))
            
            # Tire temperature
            tire_temp = 90 + (tire_wear * 0.3) + random.uniform(-5, 5)
            
            # Lap time - use actual fastest lap as reference if available
            lap_time = base_lap_time + (tire_wear * 0.1) + random.uniform(-2, 2) / consistency_modifier
            
            # Sector time
            sector_time = lap_time / 3 + random.uniform(-0.5, 0.5) / consistency_modifier
            
            # Position - maintain actual position if available, otherwise simulate
            if actual_position:
                # Small variations around actual position
                position = max(1, min(20, actual_position + int(random.uniform(-1, 1))))
            else:
                position_variation = int(random.uniform(-3, 3) - (performance_modifier / 3))
                position = max(1, min(20, start_position + position_variation + (lap // 15)))
            
            # Speed
            speed = base_speed - (tire_wear * 0.5) + random.uniform(-10, 10)
            
            # RPM
            rpm = base_rpm + (speed - 280) * 10 + random.uniform(-200, 200)
            
            timestamp = base_time + timedelta(seconds=lap * lap_time)
            
            data_points.append({
                'speed': round(speed, 2),
                'rpm': round(rpm, 0),
                'lap_time': round(lap_time, 3),
                'tire_temp': round(tire_temp, 1),
                'tire_wear': round(tire_wear, 1),
                'sector_time': round(sector_time, 3),
                'position': position,
                'timestamp': timestamp,
                'lap': lap
            })
        
        # Reset random seed
        random.seed()
        
        return data_points
    

