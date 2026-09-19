# AI-Powered Agentic Logistics Operations Copilot

A POC AI-first logistics operations assistant that investigates shipment disruptions, selects relevant investigation tools, and provides an operational recommendation with confidence and human escalation when needed.

## Overview

Logistics operations teams often need to investigate shipment delays manually by checking multiple sources before deciding what action to take.

This POC demonstrates how an agentic AI workflow can assist with this process by:

1. Assessing the current shipment condition.
2. Determining whether investigation is required.
3. Dynamically selecting the most relevant investigation tool.
4. Evaluating the investigation results.
5. Providing an operational recommendation.
6. Escalating cases to a human when the available evidence is insufficient.

The prototype uses mock shipment, weather, and carrier data to demonstrate the agentic workflow.

---

## Key Agentic Functions

### 1. Intelligent Shipment Assessment

The agent analyzes shipment information and determines:

- Severity of the disruption
- Potential cause
- Whether action is required
- Whether further investigation is necessary
- Which investigation tool should be used

### 2. Autonomous Investigation & Tool Selection

The agent dynamically selects an investigation path based on the shipment context.

Available tools:

- `check_weather`
- `check_alternate_carriers`

The agent does not automatically execute every available tool.

### 3. Recommendation & Human Escalation

After gathering additional evidence, the agent evaluates the results and provides:

- Finding
- Recommended operational action
- Confidence level
- Human review requirement

Cases with insufficient or ambiguous evidence are escalated to a human operator.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │   /analyze-shipment  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     LangGraph        │
                    │ Agent Orchestration  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   LLM Assessment     │
                    │ Gemini / OpenRouter  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │ Conditional Routing  │
                    └─────┬────────┬───────┘
                          │        │
                    ┌─────▼───┐ ┌──▼─────────────┐
                    │ Weather │ │ Alternate      │
                    │  Tool   │ │ Carrier Tool   │
                    └─────┬───┘ └──────┬─────────┘
                          │            │
                          └──────┬─────┘
                                 ▼
                    ┌──────────────────────┐
                    │ Investigation        │
                    │ Evaluation           │
                    │ LLM                  │
                    └──────────┬───────────┘
                               │
                     ┌─────────▼──────────┐
                     │ Recommendation /   │
                     │ Human Review       │
                     └────────────────────┘