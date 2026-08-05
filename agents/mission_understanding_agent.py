import os
import json
import re
from typing import Any
from dotenv import load_dotenv

# Migrate to new google-genai library
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(APP_DIR, ".env"))

api_key = os.getenv("GEMINI_API_KEY")

# New client initialization
if api_key and GENAI_AVAILABLE:
    genai_client = genai.Client(api_key=api_key)
else:
    genai_client = None

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
8. "home_latitude": Floating point number coordinate. Default is 33.6425.
9. "home_longitude": Floating point number coordinate. Default is 73.0232.

Respond ONLY with a valid JSON block enclosed in ```json and ```. Do not include any other conversational text or markdown.
"""


def parse_with_regex(user_input: str) -> dict[str, Any]:
    """
    Parses key parameters from the user request using standard regular expressions
    as a safe offline backup system.
    """
    data = {
        "mission_name": "Surveillance Mission",
        "mission_type": "surveillance",
        "altitude": 50.0,
        "duration": 15.0,
        "return_to_launch": True,
        "avoid_no_fly_zone": True,
        "route_pattern": "square",
        "home_latitude": 33.6425,
        "home_longitude": 73.0232
    }

    input_lower = user_input.lower()

    # Extract Altitude
    alt_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m|meter)', input_lower)
    if alt_match:
        data["altitude"] = float(alt_match.group(1))

    # Extract Duration
    dur_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:min|minute)', input_lower)
    if dur_match:
        data["duration"] = float(dur_match.group(1))

    # Extract Route Pattern types
    if "grid" in input_lower:
        data["route_pattern"] = "grid"
    elif "perimeter" in input_lower:
        data["route_pattern"] = "perimeter"
    elif "circle" in input_lower:
        data["route_pattern"] = "circle"

    # Extract Mission Type
    if "delivery" in input_lower:
        data["mission_type"] = "delivery"
        data["mission_name"] = "UAV Delivery Mission"
    elif "inspection" in input_lower:
        data["mission_type"] = "inspection"
        data["mission_name"] = "Infrastructure Inspection"
    elif "search" in input_lower or "rescue" in input_lower:
        data["mission_type"] = "search_and_rescue"
        data["mission_name"] = "Search and Rescue Mission"

    return data


def parse_mission_request(user_input: str) -> dict[str, Any]:
    """
    Translates user requests using Google's generative AI models,
    falling back on local regex processing if network connections or API endpoints fail.
    """
    if not api_key or not GENAI_AVAILABLE or genai_client is None:
        return parse_with_regex(user_input)

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    prompt = f"{SYSTEM_PROMPT}\n\nUser request: \"{user_input}\""

    for model_name in models_to_try:
        try:
            # New API syntax for google-genai
            response = genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            text_response = response.text.strip()
            # Clean markdown formatting tags if returned
            if text_response.startswith("```"):
                text_response = re.sub(r'^```(?:json)?\n', '', text_response)
                text_response = re.sub(r'\n```$', '', text_response)

            # Parse JSON response
            parsed_data = json.loads(text_response)
            return parsed_data
        except Exception as e:
            continue

    # Safe fallback if API calls failed or model not found
    return parse_with_regex(user_input)


def understand_mission(user_input: str) -> dict[str, Any]:
    """
    Main entry point for the Mission Understanding Agent.
    Processes user input and returns structured mission parameters.
    """
    return parse_mission_request(user_input)