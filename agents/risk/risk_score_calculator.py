import logging

logger = logging.getLogger(__name__)


class RiskScoreCalculator:
    """
    ==========================================================
    Risk Score Calculator

    Responsibility:
        Combine normalized features into a single 0-100 Risk
        Score using configured weights:

            RiskScore = Sum(feature * weight)

        Weights for features that were unavailable for this
        entity are excluded and the remaining weights are
        re-normalized, so a missing feature never silently
        drags the score toward zero.

    Input:
        Normalized Feature Dictionary

    Output:
        Risk Score (0-100)

    DOES NOT
    --------
    - Normalize features
    - Classify severity
    - Calculate probability
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Risk Score Calculator Ready.")

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, normalized_features):

        if not normalized_features:

            return 0.0

        feature_definitions = self.rule_engine.get_feature_definitions()

        weighted_sum = 0.0

        total_weight = 0.0

        for feature_name, value in normalized_features.items():

            feature_config = feature_definitions.get(feature_name, {})

            weight = feature_config.get("weight", 0.0)

            weighted_sum += value * weight

            total_weight += weight

        if total_weight == 0:

            return 0.0

        risk_fraction = weighted_sum / total_weight

        return round(risk_fraction * 100, 2)
