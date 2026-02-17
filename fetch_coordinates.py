import json
import re
import time
import urllib.parse
import sys
import argparse
import csv
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm

def setup_logging(log_level, log_file=None):
    """Setup logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def extract_coordinates_from_url(url):
    """
    Extracts latitude and longitude from a Google Maps URL.
    Returns (lat, long, source) where source indicates extraction method.
    """
    # Pattern 1: !3d-7.9!4d112.6 (Protobuf) - Prioritize this! (Pin location)
    match = re.search(r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)', url)
    if match: 
        return match.group(1), match.group(2), 'pin'
    
    # Pattern 2: !2d... (Long)!3d... (Lat)
    # Note: !3d is Lat, !2d is Long
    match_lat = re.search(r'!3d(-?\d+\.?\d*)', url)
    match_long = re.search(r'!2d(-?\d+\.?\d*)', url)
    if match_lat and match_long:
        return match_lat.group(1), match_long.group(1), 'pin'

    # Pattern 3: query param ?q=lat,long or &ll=lat,long
    match = re.search(r'[?&](?:q|ll)=(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
    if match: 
        return match.group(1), match.group(2), 'query'
            
    # Pattern 4: @lat,long (Viewport center - Fallback)
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', url)
    if match: 
        return match.group(1), match.group(2), 'viewport'
        
    return None, None, None

def validate_coordinates(lat, long):
    """
    Validate that coordinates are within valid ranges.
    Returns (is_valid, warnings)
    """
    warnings = []
    is_valid = True
    
    try:
        lat_float = float(lat)
        long_float = float(long)
        
        # Check latitude range
        if lat_float < -90 or lat_float > 90:
            warnings.append(f"Latitude {lat} out of range [-90, 90]")
            is_valid = False
        
        # Check longitude range
        if long_float < -180 or long_float > 180:
            warnings.append(f"Longitude {long} out of range [-180, 180]")
            is_valid = False
        
        # Check for suspicious coordinates
        if lat_float == 0 and long_float == 0:
            warnings.append("Coordinates are (0,0) - likely invalid")
            is_valid = False
            
    except (ValueError, TypeError):
        warnings.append(f"Invalid coordinate format: lat={lat}, long={long}")
        is_valid = False
    
    return is_valid, warnings

def get_coordinates(driver, gmaps_url, name, context=None, max_retries=3, retry_delay=5):
    """
    Attempts to get coordinates first by visiting the URL, 
    and failing that (or if URL is blocked/broken), by searching the name.
    Implements retry logic with exponential backoff.
    
    Returns: (lat, long, source) or (None, None, None)
    """
    lat, long, source = None, None, None
    
    # Strategy 1: Direct URL Visit
    if gmaps_url and len(gmaps_url) > 5:
        # Clean URL (remove trailing dots common in copy-paste errors)
        if gmaps_url.endswith('.'):
             gmaps_url = gmaps_url[:-1]
             
        for attempt in range(max_retries):
            try:
                logging.debug(f"Visiting URL (attempt {attempt + 1}/{max_retries}): {gmaps_url}")
                driver.get(gmaps_url)
                # Wait for potential redirects
                time.sleep(4) 
                final_url = driver.current_url
                
                # Check for soft-block (Google Sorry/CAPTCHA)
                if "google.com/sorry" in final_url:
                    logging.warning("Detected Google CAPTCHA/Soft-block on URL")
                    lat, long, source = None, None, None
                else:
                    lat, long, source = extract_coordinates_from_url(final_url)
                    if lat and long:
                        logging.info(f"Extracted from URL: {lat}, {long} (source: {source})")
                        return lat, long, source
                
                # If we got here without success, break retry loop for URL
                break
                        
            except Exception as e:
                logging.warning(f"Error visiting URL (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed after {max_retries} attempts")
            
    # Strategy 2: Search Query Fallback (if URL failed or coordinates not found)
    if not lat or not long:
        logging.debug(f"Fallback: Searching for '{name}'...")
        
        for attempt in range(max_retries):
            try:
                # Apply context if provided
                search_query = name
                if context and context not in name:
                    search_query += f" {context}"
                    logging.debug(f"Applied context: '{search_query}'")
                    
                query = urllib.parse.quote(search_query)
                search_url = f"https://www.google.com/maps/search/{query}"
                driver.get(search_url)
                time.sleep(5)
                
                final_url = driver.current_url
                lat, long, source = extract_coordinates_from_url(final_url)
                if lat and long:
                    logging.info(f"Extracted from search: {lat}, {long} (source: {source})")
                    return lat, long, source
                
                # If we got here without success, break retry loop
                break
                
            except Exception as e:
                logging.warning(f"Error during search (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed after {max_retries} attempts")
             
    return None, None, None

def save_to_json(data, output_file):
    """Save data to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"Saved to JSON: {output_file}")

def save_to_csv(data, output_file):
    """Save data to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['key', 'name', 'gmaps_url', 'latitude', 'longitude'])
        
        # Write data
        for key, item in data.items():
            name = item.get('name', '')
            gmaps = item.get('gmaps', '')
            latlong = item.get('latlong', {})
            lat = latlong.get('lat', '')
            long = latlong.get('long', '')
            writer.writerow([key, name, gmaps, lat, long])
    
    logging.info(f"Saved to CSV: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Extract coordinates from Google Maps URLs for any type of location.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_coordinates.py places.json
  python fetch_coordinates.py places.json --force
  python fetch_coordinates.py places.json --output-format csv
  python fetch_coordinates.py places.json --context "New York"
  python fetch_coordinates.py places.json --log-level DEBUG --log-file app.log
        """
    )
    
    parser.add_argument("input_file", help="Path to the input JSON file")
    parser.add_argument("--force", action="store_true", 
                       help="Force update all entries, even if coordinates exist")
    parser.add_argument("--output-format", choices=['json', 'csv'], default='json',
                       help="Output format (default: json)")
    parser.add_argument("--context", type=str, default=None,
                       help="Optional location context to append to searches (e.g., 'New York', 'Tokyo')")
    parser.add_argument("--max-retries", type=int, default=3,
                       help="Maximum number of retry attempts (default: 3)")
    parser.add_argument("--retry-delay", type=int, default=5,
                       help="Initial retry delay in seconds (default: 5)")
    parser.add_argument("--log-level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help="Logging level (default: INFO)")
    parser.add_argument("--log-file", type=str, default=None,
                       help="Optional log file path")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)
    
    input_file = args.input_file
    force_update = args.force
    output_format = args.output_format
    context = args.context
    max_retries = args.max_retries
    retry_delay = args.retry_delay

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: {input_file} not found.")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Error: Invalid JSON in {input_file}: {e}")
        return

    # Setup Selenium Headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # User agent to reduce bot detection
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    logging.info("Initializing Browser...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    validation_warnings = 0
    
    # Track timing
    import time as time_module
    start_time = time_module.time()
    
    logging.info(f"Processing {len(data)} entries from {input_file}...")
    if force_update:
        logging.info("FORCE UPDATE MODE: Enabled")
    if context:
        logging.info(f"Location context: '{context}'")
    
    try:
        # Use tqdm for progress bar
        with tqdm(total=len(data), desc="Processing locations", unit="location") as pbar:
            for key, item in data.items():
                name = item.get('name', 'Unknown')
                gmaps_url = item.get('gmaps', '')
                latlong = item.get('latlong', {})
                current_lat = latlong.get('lat', '')
                current_long = latlong.get('long', '')
                
                # Update progress bar description with current location
                pbar.set_description(f"Processing: {name[:30]}...")
                
                # Determine whether to process this entry
                should_process = False
                if force_update:
                    should_process = True
                elif not current_lat or not current_long:
                     should_process = True
                
                if should_process:
                    logging.debug(f"Processing: {name}")
                    
                    # Check if we have enough info to proceed
                    if not gmaps_url and not name:
                        logging.warning(f"SKIPPED: No Name or URL for key '{key}'")
                        skipped_count += 1
                        pbar.update(1)
                        continue
                    
                    new_lat, new_long, source = get_coordinates(
                        driver, gmaps_url, name, context, max_retries, retry_delay
                    )
                    
                    if new_lat and new_long:
                        # Validate coordinates
                        is_valid, warnings = validate_coordinates(new_lat, new_long)
                        
                        if warnings:
                            validation_warnings += 1
                            for warning in warnings:
                                logging.warning(f"Validation warning for '{name}': {warning}")
                        
                        # Only update if changed (optional check, but good for logs)
                        if new_lat != current_lat or new_long != current_long:
                            item['latlong']['lat'] = str(new_lat)
                            item['latlong']['long'] = str(new_long)
                            logging.info(f"UPDATED '{name}': {new_lat}, {new_long} (source: {source})")
                            updated_count += 1
                            
                            # Periodic save every 5 updates
                            if updated_count % 5 == 0:
                                save_to_json(data, input_file)
                        else:
                             logging.debug(f"No change for '{name}'")
                    else:
                        logging.error(f"FAILED: Could not resolve coordinates for '{name}'")
                        failed_count += 1
                
                pbar.update(1)
                
    except KeyboardInterrupt:
        logging.warning("\nStopping due to user interrupt...")
    finally:
        driver.quit()
        
        # Final save to JSON (always save source data)
        save_to_json(data, input_file)
        
        # Save to requested output format
        if output_format == 'csv':
            csv_file = Path(input_file).stem + '.csv'
            save_to_csv(data, csv_file)
            
    # Calculate timing statistics
    end_time = time_module.time()
    total_time = end_time - start_time
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Total Entries: {len(data)}")
    print(f"Updated: {updated_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped (No Data): {skipped_count}")
    print(f"Validation Warnings: {validation_warnings}")
    print("-" * 50)
    print(f"Total Time: {total_time:.2f}s")
    if updated_count > 0:
        avg_time = total_time / updated_count
        locations_per_min = 60 / avg_time  # 60 seconds / avg_time per location
        print(f"Average Time per Location: {avg_time:.2f}s")
        print(f"Processing Rate: {locations_per_min:.2f} locations/min")
    print("="*50)

if __name__ == "__main__":
    main()
