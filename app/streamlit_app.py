import streamlit as st

from agents.logistics_agent import logistics_graph


st.set_page_config(
    page_title="AI Logistics Operations",
    page_icon="🚚",
    layout="wide",
)


st.title("🚚 AI Logistics Operations")

st.write(
    "AI-assisted shipment investigation and "
    "operational decision support."
)


# ============================================================
# INPUT
# ============================================================

shipment_id = st.text_input(
    "Shipment ID",
    placeholder="e.g. PH-1120",
)


analyze = st.button(
    "Analyze Shipment",
    type="primary",
)


# ============================================================
# ANALYZE
# ============================================================

if analyze:

    if not shipment_id:
        st.warning("Please enter a shipment ID.")

    else:

        with st.spinner("Analyzing shipment..."):

            result = logistics_graph.invoke({
                "shipment_id": shipment_id.strip()
            })


        # ====================================================
        # SHIPMENT
        # ====================================================

        st.subheader("Shipment")

        shipment = result.get(
            "shipment",
            {}
        )

        if not shipment.get("found", False):

            st.error(
                f"Shipment {shipment_id} was not found."
            )

        else:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Status",
                shipment.get("status", "Unknown")
            )

            col2.metric(
                "Location",
                shipment.get("location", "Unknown")
            )

            col3.metric(
                "Origin",
                shipment.get("origin", "Unknown")
            )

            col4.metric(
                "Destination",
                shipment.get("destination", "Unknown")
            )


            delay = shipment.get(
                "delay_minutes"
            )

            if delay is not None:
                st.metric(
                    "Delay",
                    f"{delay} minutes"
                )


        # ====================================================
        # ASSESSMENT
        # ====================================================

        st.divider()

        st.subheader("🤖 Shipment Assessment")

        assessment = result.get(
            "assessment",
            {}
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Severity",
            assessment.get(
                "severity",
                "Unknown"
            ).upper()
        )

        col2.metric(
            "Cause",
            assessment.get(
                "cause",
                "Unknown"
            ).upper()
        )

        col3.metric(
            "Investigation",
            (
                "Required"
                if assessment.get(
                    "investigation_required",
                    False
                )
                else "Not Required"
            )
        )

        st.write(
            "**Reason:**",
            assessment.get(
                "reason",
                "No assessment available."
            )
        )


        # ====================================================
        # INVESTIGATION
        # ====================================================

        st.divider()

        st.subheader("🔎 Investigation")

        tools_used = result.get(
            "tools_used",
            []
        )

        tools_skipped = result.get(
            "tools_skipped",
            []
        )

        if tools_used:

            st.write("**Tools used:**")

            for tool in tools_used:
                st.success(
                    f"✓ {tool}"
                )

        else:

            st.info(
                "No investigation tools were required."
            )


        # Weather result

        weather_result = result.get(
            "weather_result"
        )

        if weather_result:

            st.write("### Weather Investigation")

            if weather_result.get(
                "alert",
                False
            ):

                st.warning(
                    weather_result.get(
                        "event",
                        "Weather alert"
                    )
                )

                col1, col2 = st.columns(2)

                col1.write(
                    "**Severity:** "
                    + str(
                        weather_result.get(
                            "severity",
                            "Unknown"
                        )
                    ).upper()
                )

                col2.write(
                    "**Affected area:** "
                    + str(
                        weather_result.get(
                            "affected_area",
                            "Unknown"
                        )
                    )
                )

                st.write(
                    weather_result.get(
                        "impact",
                        ""
                    )
                )

            else:

                st.success(
                    "No significant weather "
                    "disruption detected."
                )


        # Carrier result

        carrier_result = result.get(
            "carrier_result"
        )

        if carrier_result:

            st.write("### Alternate Carrier Investigation")

            options = carrier_result.get(
                "options",
                []
            )

            if options:

                for option in options:

                    st.write(
                        f"**{option.get('carrier')}**"
                    )

                    st.write(
                        f"Route: "
                        f"{option.get('route')}"
                    )

                    st.write(
                        f"ETA improvement: "
                        f"{option.get('eta_improvement_days')} days"
                    )

                    st.divider()

            else:

                st.info(
                    "No alternate carrier options found."
                )


        # ====================================================
        # RECOMMENDATION
        # ====================================================

        st.divider()

        st.subheader("💡 Recommendation")

        recommendation = result.get(
            "recommendation",
            "No recommendation available."
        )

        st.info(
            recommendation
        )


        # ====================================================
        # CONFIDENCE / HUMAN REVIEW
        # ====================================================

        col1, col2 = st.columns(2)

        confidence = result.get(
            "confidence",
            "low"
        )

        human_review = result.get(
            "human_review",
            False
        )

        col1.metric(
            "Confidence",
            confidence.upper()
        )

        col2.metric(
            "Human Review",
            "Required"
            if human_review
            else "Not Required"
        )


        # ====================================================
        # DEBUG / AGENT TRACE
        # ====================================================

        with st.expander(
            "View Agent Trace"
        ):

            st.json({
                "shipment_id": shipment_id,
                "assessment": assessment,
                "tools_used": tools_used,
                "tools_skipped": tools_skipped,
                "weather_result": weather_result,
                "carrier_result": carrier_result,
                "recommendation": recommendation,
                "confidence": confidence,
                "human_review": human_review,
            })