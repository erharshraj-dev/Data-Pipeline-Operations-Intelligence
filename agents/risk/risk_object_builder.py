import logging

logger = logging.getLogger(__name__)


class RiskObjectBuilder:
    """
    -------------------------------------------------------
    Risk Object Builder

    Responsibility:
    Build the final Risk Object from the Risk Prediction
    Agent's analysis outputs.

    Input:
        Behavior Object
        Risk Analysis Dictionary

    Output:
        Risk Object

    NOTE:
        By explicit specification, the Risk Object contains
        ONLY entity_id, risk_score, risk_severity,
        risk_probability, risk_category, and
        prediction_confidence. Unlike the Observation Object
        and Behavior Object, it deliberately carries no
        metadata block and no reference back to its inputs.
    -------------------------------------------------------
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        logger.info("Risk Object Builder Ready.")

    # =====================================================
    # BUILD RISK OBJECT
    # =====================================================

    def build(self, behavior_object, risk_analysis):

        risk_object = {

            "entity_id": behavior_object.get("entity_id"),

            "risk_score": risk_analysis["risk_score"],

            "risk_severity": risk_analysis["risk_severity"],

            "risk_probability": risk_analysis["risk_probability"],

            "risk_category": risk_analysis["risk_category"],

            "prediction_confidence": risk_analysis["prediction_confidence"]

        }

        return risk_object
