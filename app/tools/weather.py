def check_weather(location: str):
    """
    Check for active weather disruptions in the shipment area.

    Mock implementation for the POC.
    """

    location = location.lower()

    if "baguio" in location or "luzon" in location:
        return {
            "alert": True,
            "event": "Severe Tropical Storm",
            "severity": "high",
            "affected_area": "Northern Luzon",
            "impact": (
                "Heavy rainfall, flooding, and hazardous road "
                "conditions are affecting major routes."
            ),
        }

    return {
        "alert": False,
        "event": None,
        "severity": None,
        "affected_area": None,
        "impact": "No significant weather disruption detected.",
    }