import os
import json
import re
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Find .env inside the current app directory or root
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(APP_DIR, ".env"))

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
You are the Mission Understanding Agent for an Agentic UAV Mission Planner.
Your job is to parse a user's natural language request for a UAV mission and convert it into a structured JSON object.

Extract or infer the following parameters from the text:
1. "mission_name": Create a short, descriptive name (e.g., "Surveillance Mission").
2. "mission_type": One of: "surveillance", "delivery", "inspection", "search_and_rescue". Default is "surveillance".
3. "altitude": UAV flying altitude in meters (number). Default is 50.0.
4. "duration": Target flight duration in minutes (number). Default is 15.0.
5. "return_to_launch": Boolean. True if the user mentions returning, RTL, landing at start, or similar. Default is True.
6. "avoid_no_fly_zone": Boolean. True if the user mentions avoiding restricted zones, no-fly zones, geofence, or security areas. Default is True.
7. "route_pattern": One of: "square", "grid", "circle", "perimeter", "manual". Default is "square".
8. "home_latitude": Latitude coordinate if mentioned (number). Default is null.
9. "home_longitude": Longitude coordinate if mentioned (number). Default is null.

Provide ONLY the valid JSON object in your response. No explanation, no markdown tags.
"""

def parse_with_regex(text: str) -> Dict[str, Any]:
    """Fallback parser using regex in case Gemini API is not available or fails."""
    text_lower = text.lower()
    
    # Mission type
    m_type = "surveillance"
    if "delivery" in text_lower or "drop" in text_lower or "transport" in text_lower:
        m_type = "delivery"
    elif "inspect" in text_lower or "check" in text_lower or "monitor" in text_lower:
        m_type = "inspection"
    elif "search" in text_lower or "rescue" in text_lower:
        m_type = "search_and_rescue"
        
    # Route pattern
    pattern = "square"
    if "grid" in text_lower or "lawnmower" in text_lower or "scan" in text_lower:
        pattern = "grid"
    elif "circle" in text_lower or "orbit" in text_lower or "circular" in text_lower:
        pattern = "circle"
    elif "perimeter" in text_lower or "boundary" in text_lower or "border" in text_lower:
        pattern = "perimeter"
    elif "manual" in text_lower or "custom" in text_lower:
        pattern = "manual"
        
    # Altitude (e.g., "below 80 meters", "at 60m", "altitude of 70 meters")
    altitude = 50.0
    alt_match = re.search(r'(?:altitude|alt|height|above)\s*(?:of|below|above|at)?\s*(\d+(?:\.\d+)?)\s*(?:m|meter|meters)?', text_lower)
    if not alt_match:
        alt_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters)\b', text_lower)
    if alt_match:
        try:
            altitude = float(alt_match.group(1))
        except ValueError:
            pass
            
    # Duration (e.g., "for 20 minutes", "20 mins", "duration 15 min")
    duration = 15.0
    dur_match = re.search(r'(?:duration|time|for|fly)\s*(\d+(?:\.\d+)?)\s*(?:min|mins|minute|minutes)', text_lower)
    if dur_match:
        try:
            duration = float(dur_match.group(1))
        except ValueError:
            pass
            
    # Return to launch
    rtl = True
    if "no rtl" in text_lower or "do not return" in text_lower or "land immediately" in text_lower:
        rtl = False
        
    # Avoid no-fly zones
    avoid_nfz = True
    if "ignore no fly" in text_lower or "enter restricted" in text_lower:
        avoid_nfz = False
        
    # Coordinates (search for lat, lon coordinates like "33.6425, 73.0232" or "lat 33.64 lon 73.02")
    lat, lon = None, None
    coord_match = re.search(r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)', text_lower)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(2))
        except ValueError:
            pass
            
    return {
        "mission_name": f"{m_type.capitalize()} Mission",
        "mission_type": m_type,
        "altitude": altitude,
        "duration": duration,
        "return_to_launch": rtl,
        "avoid_no_fly_zone": avoid_nfz,
        "route_pattern": pattern,
        "home_latitude": lat,
        "home_longitude": lon
    }

def understand_mission(user_input: str) -> Dict[str, Any]:
    """
    Parses natural language user inputs to extract key UAV mission parameters.
    Uses Gemini 1.5 Flash if available, with a regex fallback for reliability.
    """
    if not user_input or len(user_input.strip()) == 0:
        return parse_with_regex("")
        
    if not api_key:
        # Fallback if API key is not configured
        return parse_with_regex(user_input)
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # We start chat session or send message directly
        prompt = f"{SYSTEM_PROMPT}\n\nUser request: \"{user_input}\""
        response = model.generate_content(prompt)
        
        text_response = response.text.strip()
        # Clean markdown wrappers if returned
        if text_response.startswith("```"):
            # strip off ```json and ```
            text_response = re.sub(r'^```(?:json)?', '', text_response)
            text_response = re.sub(r'```$', '', text_response)
            text_response = text_response.strip()
            
        parsed_json = json.loads(text_response)
        
        # Verify schema
        required_keys = ["mission_name", "mission_type", "altitude", "duration", 
                         "return_to_launch", "avoid_no_fly_zone", "route_pattern", 
                         "home_latitude", "home_longitude"]
        for key in required_keys:
            if key not in parsed_json:
                # Add default or fallback value
                fallback_data = parse_with_regex(user_input)
                parsed_json[key] = fallback_data[key]
                
        return parsed_json
        
    except Exception as e:
        print(f"Gemini understanding error: {e}. Using regex fallback.")
        return parse_with_regex(user_input)
