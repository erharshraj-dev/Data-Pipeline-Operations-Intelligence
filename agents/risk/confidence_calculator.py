import logging

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """
    ==========================================================
    Confidence Calculator

    Responsibility:
        Estimate Prediction Confidence by blending the
        Behavior Agent's own confidence with how many of the
        configured risk features were actually available for
        this entity.

    Input:
        Raw Feature Dictionary, Behavior Confidence

    Output:
        Prediction Confidence (0.0 - 1.0)

    DOES NOT
    --------
    - Extract features
    - Calculate risk score or probability
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        self.confidence_config = self.rule_engine.get_confidence_config()

        logger.info("Confidence Calculator Ready.")

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, raw_features, behavior_confidence):

        feature_definitions = self.rule_engine.get_feature_definitions()

        total_configured = len(feature_definitions)

        available = len(raw_features)

        if total_configured > 0:

            feature_completeness = available / total_configured

        else:

            feature_completeness = 0.0

        behavior_confidence_weight = self.confidence_config.get(
            "behavior_confidence_weight", 0.5
        )

        feature_completeness_weight = self.confidence_config.get(
            "feature_completeness_weight", 0.5
        )

        minimum_confidence = self.confidence_config.get(
            "minimum_confidence", 0.0
        )

        maximum_confidence = self.confidence_config.get(
            "maximum_confidence", 1.0
        )

        behavior_confidence = behavior_confidence or 0.0

        confidence = (

            (behavior_confidence * behavior_confidence_weight) +

            (feature_completeness * feature_completeness_weight)

        )

        confidence = max(

            minimum_confidence,

            min(confidence, maximum_confidence)

        )

        return round(confidence, 2)
