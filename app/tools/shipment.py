SHIPMENTS = {
    "PH-1120": {
        "status": "delayed",
        "location": "Baguio",
        "origin": "Manila",
        "destination": "Baguio",
        "delay_minutes": 240,
    },
    "PH-4521": {
        "status": "held",
        "location": "Port of Manila",
        "origin": "Manila",
        "destination": "Cebu",
        "delay_minutes": None,
    },
    "PH-2201": {
        "status": "delayed",
        "location": "Quezon City",
        "origin": "Manila",
        "destination": "Quezon City",
        "delay_minutes": 25,
    },
    "PH-7789": {
        "status": "unknown",
        "location": "Unknown",
        "origin": "Unknown",
        "destination": "Unknown",
        "delay_minutes": None,
    },
}


def get_shipment(shipment_id: str):
    """
    Retrieve shipment information from our mock Philippine
    logistics management system.
    """

    shipment = SHIPMENTS.get(shipment_id)

    if not shipment:
        return {
            "found": False,
            "shipment_id": shipment_id,
            "message": "Shipment not found",
        }

    return {
        "found": True,
        "shipment_id": shipment_id,
        **shipment,
    }