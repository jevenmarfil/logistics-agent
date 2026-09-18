import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from llm import generate_llm_response

from tools.shipment import get_shipment
from tools.weather import check_weather
from tools.carriers import check_alternate_carriers


class LogisticsState(TypedDict, total=False):
    shipment_id: str
    shipment: dict
    assessment: dict

    investigation_tool: str
    investigation_reason: str

    weather_result: dict
    carrier_result: dict

    tools_used: list
    tools_skipped: list

    recommendation: str
    confidence: str
    human_review: bool


def parse_json_response(response_text: str):
    cleaned = response_text.strip()

    # Remove markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Find the JSON object if the model added surrounding text
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            f"No JSON object found in LLM response: {cleaned}"
        )

    cleaned = cleaned[start:end + 1]

    return json.loads(cleaned)

# ============================================================
# LLM #1 - Initial Shipment Assessment
# ============================================================

def llm_assess_shipment(shipment: dict):
    prompt = f"""
You are a logistics operations analyst for a Philippine logistics company.

Analyze the following shipment data:

{shipment}

Your task is to assess the current shipment condition and determine
whether further investigation is required.

Return ONLY valid JSON using exactly this structure:

{{
    "severity": "minor|moderate|high|unknown",
    "cause": "weather|customs|carrier|operational_delay|unknown",
    "action_required": true,
    "investigation_required": true,
    "investigation_tool": "check_weather|check_alternate_carriers|none|human_review",
    "reason": "short explanation"
}}

Rules:

1. Severity
- Delays under 60 minutes with no other issue are usually minor.
- Delays of 60 minutes or more should generally be investigated.
- Significant operational disruptions should be moderate or high.
- Unknown shipment status or insufficient information should be unknown.

2. Cause
- Severe weather, flooding, tropical storms, or hazardous roads
  should generally be classified as weather.
- Customs or port holds should generally be classified as customs.
- Carrier or shipping-line problems should generally be classified as carrier.
- Short operational delays can be classified as operational_delay.
- If the cause cannot be determined from the shipment data,
  use unknown.

3. Investigation tool selection
- Use check_weather when weather could plausibly explain the
  disruption based on the shipment location or available shipment
  information.
- Use check_alternate_carriers for carrier issues, customs or port
  holds, or routing problems where alternative transportation may
  be relevant.
- Use none when no investigation is necessary.
- Use human_review only when there is insufficient information to
  determine which investigation path is appropriate.

Important:
- An unknown cause does NOT automatically mean human_review.
- If enough information exists to select a reasonable investigation
  tool, select that tool.
- For a significant delay with an unknown cause, use the shipment
  location and available information to select an appropriate
  investigation tool.
- If the location is Baguio or Northern Luzon and the cause is
  unknown, use check_weather.

4. Important
- Do not invent information.
- Base the assessment only on the shipment data provided.
- A significant delay with an unknown cause should generally require
  investigation rather than immediately going to human review.

Return JSON only.
"""

    return generate_llm_response(prompt)


# ============================================================
# LLM #2 - Evaluate Investigation
# ============================================================

def llm_evaluate_investigation(
    shipment: dict,
    assessment: dict,
    investigation_result: dict,
):
    prompt = f"""
You are a logistics operations decision-support agent for a
Philippine logistics company.

Original shipment data:

{shipment}

Initial shipment assessment:

{assessment}

Investigation result:

{investigation_result}

Evaluate the new evidence and determine the appropriate operational
recommendation.

Return ONLY valid JSON using exactly this structure:

{{
    "finding": "short explanation of what the investigation discovered",
    "recommendation": "recommended operational action",
    "confidence": "low|medium|high",
    "human_review": false
}}

Rules:

- Base the recommendation on the shipment data and investigation result.
- Do not invent information.
- If the investigation provides strong evidence for the cause,
  confidence can be high.
- If evidence is incomplete or ambiguous, use medium or low confidence.
- If there is insufficient evidence to safely recommend an action,
  set human_review to true.
- Do not recommend rerouting when the evidence indicates that the
  broader route or destination is affected.
- For minor issues, a no-action recommendation is acceptable.

Return JSON only.
"""

    return generate_llm_response(prompt)


# ============================================================
# NODE 1 - Retrieve + Assess Shipment
# ============================================================

def assess_status(state: LogisticsState):
    """
    Retrieve the shipment and perform the initial LLM assessment.
    """

    shipment_id = state["shipment_id"]

    shipment = get_shipment(shipment_id)

    # Shipment not found
    if not shipment["found"]:
        return {
            "shipment": shipment,
            "assessment": {
                "severity": "unknown",
                "cause": "unknown",
                "action_required": False,
                "investigation_required": False,
                "investigation_tool": "human_review",
                "reason": "Shipment was not found.",
            },
            "confidence": "low",
            "human_review": True,
        }

    try:
        response_text = llm_assess_shipment(
            shipment
        )

        assessment = parse_json_response(
            response_text
        )

    except Exception as e:
        return {
            "shipment": shipment,
            "assessment": {
                "severity": "unknown",
                "cause": "unknown",
                "action_required": False,
                "investigation_required": False,
                "investigation_tool": "human_review",
                "reason": (
                    f"Shipment assessment failed: {str(e)}"
                ),
            },
            "confidence": "low",
            "human_review": True,
        }

    return {
        "shipment": shipment,
        "assessment": assessment,
    }


# ============================================================
# ROUTER
# ============================================================

def route_after_assessment(state: LogisticsState):
    assessment = state.get(
        "assessment",
        {}
    )

    if state.get("human_review"):
        return "human_review"

    investigation_required = assessment.get(
        "investigation_required",
        False,
    )

    if not investigation_required:
        return "minor"

    investigation_tool = assessment.get(
        "investigation_tool"
    )

    if investigation_tool == "check_weather":
        return "weather"

    if investigation_tool == "check_alternate_carriers":
        return "carrier"

    if investigation_tool == "human_review":
        return "human_review"

    return "human_review"


# ============================================================
# WEATHER INVESTIGATION
# ============================================================

def investigate_weather(state: LogisticsState):
    shipment = state["shipment"]

    result = check_weather(
        shipment["location"]
    )

    tools_used = state.get(
        "tools_used",
        []
    )

    return {
        "weather_result": result,
        "tools_used": tools_used + [
            "check_weather"
        ],
        "tools_skipped": state.get(
            "tools_skipped",
            []
        ),
    }


# ============================================================
# CARRIER INVESTIGATION
# ============================================================

def investigate_carriers(state: LogisticsState):
    shipment = state["shipment"]

    result = check_alternate_carriers(
        shipment["origin"],
        shipment["destination"],
    )

    tools_used = state.get(
        "tools_used",
        []
    )

    return {
        "carrier_result": result,
        "tools_used": tools_used + [
            "check_alternate_carriers"
        ],
        "tools_skipped": state.get(
            "tools_skipped",
            []
        ),
    }


# ============================================================
# FINAL LLM EVALUATION
# ============================================================

def evaluate_investigation(state: LogisticsState):
    shipment = state["shipment"]
    assessment = state["assessment"]

    if state.get("weather_result"):
        investigation_result = state[
            "weather_result"
        ]

    elif state.get("carrier_result"):
        investigation_result = state[
            "carrier_result"
        ]

    else:
        return {
            "recommendation": (
                "Insufficient investigation evidence "
                "to make a recommendation."
            ),
            "confidence": "low",
            "human_review": True,
        }

    try:
        response_text = llm_evaluate_investigation(
            shipment,
            assessment,
            investigation_result,
        )

        result = parse_json_response(
            response_text
        )

        return {
            "recommendation": result.get(
                "recommendation"
            ),
            "confidence": result.get(
                "confidence",
                "low",
            ),
            "human_review": result.get(
                "human_review",
                False,
            ),
        }

    except Exception as e:
        return {
            "recommendation": (
                f"Final evaluation failed: {str(e)}"
            ),
            "confidence": "low",
            "human_review": True,
        }


# ============================================================
# HUMAN REVIEW
# ============================================================

def human_review(state: LogisticsState):
    return {
        "recommendation": (
            "Insufficient information to make a "
            "confident recommendation. "
            "Flagged for human review."
        ),
        "confidence": "low",
        "human_review": True,
    }


# ============================================================
# NO INVESTIGATION
# ============================================================

def no_investigation(state: LogisticsState):
    assessment = state.get(
        "assessment",
        {}
    )

    reason = assessment.get(
        "reason",
        "No significant issue requiring "
        "investigation was detected.",
    )

    return {
        "recommendation": (
            f"No investigation required. {reason}"
        ),
        "confidence": "high",
        "human_review": False,
        "tools_used": state.get(
            "tools_used",
            []
        ),
        "tools_skipped": [
            "check_weather",
            "check_alternate_carriers",
        ],
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_graph():
    graph = StateGraph(
        LogisticsState
    )

    graph.add_node(
        "assess_status",
        assess_status
    )

    graph.add_node(
        "investigate_weather",
        investigate_weather
    )

    graph.add_node(
        "investigate_carriers",
        investigate_carriers
    )

    graph.add_node(
        "evaluate_investigation",
        evaluate_investigation
    )

    graph.add_node(
        "no_investigation",
        no_investigation
    )

    graph.add_node(
        "human_review",
        human_review
    )

    graph.add_edge(
        START,
        "assess_status"
    )

    graph.add_conditional_edges(
        "assess_status",
        route_after_assessment,
        {
            "minor": "no_investigation",
            "weather": "investigate_weather",
            "carrier": "investigate_carriers",
            "human_review": "human_review",
        },
    )

    graph.add_edge(
        "investigate_weather",
        "evaluate_investigation",
    )

    graph.add_edge(
        "investigate_carriers",
        "evaluate_investigation",
    )

    graph.add_edge(
        "evaluate_investigation",
        END,
    )

    graph.add_edge(
        "no_investigation",
        END,
    )

    graph.add_edge(
        "human_review",
        END,
    )

    return graph.compile()


logistics_graph = build_graph()