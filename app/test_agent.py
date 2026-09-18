from agents.logistics_agent import logistics_graph


test_cases = [
    "PH-1120",
    # "PH-4521",
    # "PH-2201",
    # "PH-7789",
]

for shipment_id in test_cases:

    print("\n" + "=" * 70)
    print("SHIPMENT:")
    print(shipment_id)

    result = logistics_graph.invoke({
        "shipment_id": shipment_id
    })

    print("\nASSESSMENT:")
    print(result.get("assessment"))

    print("\nSHIPMENT DATA:")
    print(result.get("shipment"))

    print("\nTOOLS USED:")
    print(result.get("tools_used", []))

    print("\nTOOLS SKIPPED:")
    print(result.get("tools_skipped", []))

    print("\nWEATHER RESULT:")
    print(result.get("weather_result"))

    print("\nCARRIER RESULT:")
    print(result.get("carrier_result"))

    print("\nRECOMMENDATION:")
    print(result.get("recommendation"))

    print("\nCONFIDENCE:")
    print(result.get("confidence"))

    print("\nHUMAN REVIEW:")
    print(result.get("human_review"))