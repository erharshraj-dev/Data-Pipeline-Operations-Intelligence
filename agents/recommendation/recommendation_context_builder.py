import logging

logger = logging.getLogger(__name__)


class RecommendationContextBuilder:
    """
    ==========================================================
    Recommendation Context Builder

    Responsibility:
        Extract every signal the Recommendation Engine, Prompt
        Builder, and Knowledge Retriever need into one flat
        dictionary, pulled from the real Behavior Object, Risk
        Object, Integrity Object, and Operational Entity shapes
        actually produced by the earlier agents.

    Input:
        Behavior Object
        Risk Object
        Integrity Object
        Operational Entity (optional — the Behavior Object
        already carries it under observation.entity; pass this
        explicitly only to evaluate against a different or
        overridden entity than the one embedded, same pattern
        used by the Integrity Agent)

    Output:
        Recommendation Context Dictionary

    DOES NOT
    --------
    - Calculate priority
    - Estimate impact / recovery time / automation
    - Retrieve knowledge
    - Call Gemini
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Recommendation Context Builder Ready.")

    # =====================================================
    # DERIVE DRIFT STATUS
    #
    # Same derivation as workflows/main.py's format_drift_status:
    # any metric flagged is_drifting -> DETECTED, else CLEAR.
    # =====================================================

    def derive_drift_status(self, behavior):

        drift = behavior.get("drift", {})

        if not drift:

            return "UNKNOWN"

        if any(result.get("is_drifting") for result in drift.values()):

            return "DETECTED"

        return "CLEAR"

    # =====================================================
    # DERIVE DEVIATION SCORE
    #
    # Same derivation as workflows/main.py's
    # format_deviation_score: the largest absolute per-metric
    # deviation percentage.
    # =====================================================

    def derive_deviation_score(self, behavior):

        deviation = behavior.get("deviation", {})

        deviations = [

            abs(result["deviation_percent"])

            for result in deviation.values()

            if result.get("deviation_percent") is not None

        ]

        if not deviations:

            return None

        return max(deviations)

    # =====================================================
    # BUILD
    # =====================================================

    def build(
        self,
        behavior_object,
        risk_object,
        integrity_object,
        operational_entity=None
    ):

        behavior = behavior_object.get("behavior", {})

        observation_object = behavior_object.get("observation", {})

        entity = (
            operational_entity
            if operational_entity is not None
            else observation_object.get("entity", {})
        )

        business_context = entity.get(
            "context", {}
        ).get(
            "business_context", {}
        )

        risk_object = risk_object or {}

        integrity_object = integrity_object or {}

        context = {

            # Operational Entity
            "entity_id": behavior_object.get("entity_id"),
            "pipeline_name": entity.get("entity_name"),
            "platform": entity.get("source_system"),
            "execution_status": entity.get("execution_status"),
            "business_criticality": business_context.get("criticality"),
            "timestamp": entity.get("event_timestamp"),

            # Behavior Object
            "behavior_score": behavior.get("behavior_score"),
            "behavior_severity": behavior.get("severity"),
            "behavior_confidence": behavior.get("confidence"),
            "deviation_score": self.derive_deviation_score(behavior),
            "drift_status": self.derive_drift_status(behavior),
            "detected_pattern": behavior.get("patterns", []) or [],

            # Risk Object
            "risk_score": risk_object.get("risk_score"),
            "risk_severity": risk_object.get("risk_severity"),
            "risk_probability": risk_object.get("risk_probability"),
            "risk_category": risk_object.get("risk_category"),

            # Recommendation Category — the Risk Prediction
            # Agent's CategoryClassifier already deterministically
            # classifies every entity (Pipeline Failure, SLA
            # Breach, Resource Exhaustion, Dependency Failure,
            # Data Quality Risk, Infrastructure Risk,
            # Configuration Risk, Operational Risk). The
            # Recommendation Agent reuses that classification as
            # its own Recommendation Category instead of running a
            # second, duplicate, LLM-free classifier.
            "category": risk_object.get("risk_category"),

            "prediction_confidence": risk_object.get(
                "prediction_confidence"
            ),

            # Integrity Object
            "integrity_score": integrity_object.get("integrity_score"),
            "integrity_status": integrity_object.get("integrity_status"),
            "output_trust_level": integrity_object.get(
                "output_trust_level"
            ),
            "primary_failure_reason": integrity_object.get(
                "primary_failure_reason"
            ),

        }

        return context
