                                                                                                                                                                                 
# 1. search_flights()                                                                                                                                                            
# Accepts the user's natural-language request, such as Flights from Bangalore to Japan.                                                                                          
                                                                                                                                                                                 
                                                                                                                                                                                 
# 2. parse_route() and resolve_airport()                                                                                                                                         
# Identify the departure and destination, then convert them into airport codes such as BLR and NRT.                                                                              
                                                                                                                                                                                 
                                                                                                                                                                                 
# 3. AviationStack API                                                                                                                                                           
# Sends an HTTP request with the API key and any recognized airport filters.                                                                                                     
                                                                                                                                                                                 
                                                                                                                                                                                 
# 4. format_flight()                                                                                                                                                             
# Converts the API response into readable flight details, including status, scheduled departure, terminal, gate, and delay.                                                      
                                                                                                                                                                                 
                                                                                                                                                                                
import os
import re
import requests
import airportsdata
from dotenv import load_dotenv

# Load API key and settings from the .env file
load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
DEFAULT_ORIGIN = os.getenv("DEFAULT_ORIGIN_IATA", "BLR")

API_URL = "https://api.aviationstack.com/v1/flights"

# Load airport information using IATA codes
AIRPORTS = airportsdata.load("IATA")


# Common city names and their main airports
CITY_AIRPORTS = {
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "delhi": "DEL",
    "mumbai": "BOM",
    "kolkata": "CCU",
    "chennai": "MAA",
    "dhaka": "DAC",
    "tokyo": "NRT",
    "osaka": "KIX",
    "new york": "JFK",
    "london": "LHR",
    "dubai": "DXB",
    "singapore": "SIN",
    "bangkok": "BKK",
    "paris": "CDG",
    "sydney": "SYD",
}


# Common country names and their main airports
COUNTRY_AIRPORTS = {
    "india": "DEL",
    "bangladesh": "DAC",
    "japan": "NRT",
    "usa": "JFK",
    "america": "JFK",
    "united states": "JFK",
    "uk": "LHR",
    "united kingdom": "LHR",
    "uae": "DXB",
    "china": "PEK",
    "singapore": "SIN",
    "malaysia": "KUL",
    "thailand": "BKK",
    "nepal": "KTM",
    "qatar": "DOH",
    "australia": "SYD",
    "canada": "YYZ",
    "germany": "FRA",
    "france": "CDG",
    "italy": "FCO",
    "spain": "MAD",
}


def clean_text(text):
    """Convert text to lowercase and remove unnecessary symbols."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_airport(location):
    """
    Convert an airport code, city, or country into an IATA code.

    Examples:
        BLR       -> BLR
        Bangalore -> BLR
        Japan     -> NRT
    """
    location = clean_text(location)

    # Check whether the user entered an airport code
    if location.upper() in AIRPORTS:
        return location.upper()

    # Check our city and country dictionaries
    if location in CITY_AIRPORTS:
        return CITY_AIRPORTS[location]

    if location in COUNTRY_AIRPORTS:
        return COUNTRY_AIRPORTS[location]

    # Search the airport database for a matching city or airport name
    for code, airport in AIRPORTS.items():
        city = airport.get("city", "").lower()
        name = airport.get("name", "").lower()

        if location == city or location == name:
            return code

    # Return None if no airport was found
    return None


def parse_route(query):
    """
    Extract departure and arrival airports from the user's query.

    Examples:
        Flights from Bangalore to Japan -> BLR, NRT
        Flights from Bangalore        -> BLR, None
        Flights to Japan               -> None, NRT
        Japan trip                     -> BLR, NRT
        All global flights             -> None, None
    """
    query = clean_text(query)

    # Handle requests for worldwide flight information
    if any(word in query for word in [
        "all country",
        "all countries",
        "all flights",
        "global flights",
        "worldwide flights",
    ]):
        return None, None

    # Extract the text after "from" and "to"
    match = re.search(
        r"\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+on\b|\s+for\b|$)",
        query,
    )

    if match:
        departure = resolve_airport(match.group(1))
        arrival = resolve_airport(match.group(2))
        return departure, arrival

    # Handle queries such as "Flights to Japan from Bangalore"
    match = re.search(
        r"\bto\s+(.+?)\s+from\s+(.+?)(?:\s+on\b|\s+for\b|$)",
        query,
    )

    if match:
        arrival = resolve_airport(match.group(1))
        departure = resolve_airport(match.group(2))
        return departure, arrival

    # Handle queries containing only a departure airport
    match = re.search(r"\bfrom\s+(.+)", query)

    if match:
        return resolve_airport(match.group(1)), None

    # Handle queries containing only a destination
    match = re.search(r"\bto\s+(.+)", query)

    if match:
        return None, resolve_airport(match.group(1))

    # If the user mentions a known city or country without "from" or "to,
    # treat it as the destination.
    for location in sorted(
        list(CITY_AIRPORTS) + list(COUNTRY_AIRPORTS),
        key=len,
        reverse=True,
    ):
        if re.search(rf"\b{re.escape(location)}\b", query):
            return DEFAULT_ORIGIN, resolve_airport(location)

    # No route could be identified
    return None, None


def format_flight(flight):
    """Format one flight into an easy-to-read text report."""

    airline = flight.get("airline") or {}
    flight_info = flight.get("flight") or {}
    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}

    return f"""
Airline: {airline.get('name', 'Unknown')}
Flight Number: {flight_info.get('iata', 'Unknown')}
Status: {flight.get('flight_status', 'Unknown')}

Departure:
  Airport: {departure.get('airport', 'Unknown')}
  Code: {departure.get('iata', 'Unknown')}
  Terminal: {departure.get('terminal') or 'N/A'}
  Gate: {departure.get('gate') or 'N/A'}
  Scheduled: {departure.get('scheduled') or 'Unknown'}
  Delay: {departure.get('delay', 'N/A')} minutes

Arrival:
  Airport: {arrival.get('airport', 'Unknown')}
  Code: {arrival.get('iata', 'Unknown')}
  Terminal: {arrival.get('terminal') or 'N/A'}
  Gate: {arrival.get('gate') or 'N/A'}
  Scheduled: {arrival.get('scheduled') or 'Unknown'}
  Delay: {arrival.get('delay', 'N/A')} minutes
""".strip()


def search_flights(query, limit=10):
    """Fetch flight information from the AviationStack API."""

    # Make sure the API key is configured
    if not API_KEY:
        return "Error: AVIATIONSTACK_API_KEY is missing from your .env file."

    # Identify the departure and arrival airports
    departure, arrival = parse_route(query)

    # Prepare the API request
    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if departure:
        params["dep_iata"] = departure

    if arrival:
        params["arr_iata"] = arrival

    try:
        # Send the request to AviationStack
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        result = response.json()

    except requests.exceptions.RequestException as error:
        return f"API request failed: {error}"

    except ValueError:
        return "Error: The API returned invalid JSON."

    # Handle errors returned by the API
    if "error" in result:
        return f"API error: {result['error'].get('message', 'Unknown error')}"

    # Get the list of flights
    flights = result.get("data", [])

    if not flights:
        return "No flight data found for the requested route."

    # Create a heading describing the search
    if departure and arrival:
        heading = f"Flights from {departure} to {arrival}"
    elif departure:
        heading = f"Flights departing from {departure}"
    elif arrival:
        heading = f"Flights arriving at {arrival}"
    else:
        heading = "Global flight information"

    # Format and display each flight
    reports = [format_flight(flight) for flight in flights[:limit]]

    return heading + "\n\n" + "\n\n---\n\n".join(reports)


# Run the program
if __name__ == "__main__":
    print(search_flights("Flights from Bangalore to Japan"))
    print("\n" + "=" * 50 + "\n")
    print(search_flights("All global flights"))