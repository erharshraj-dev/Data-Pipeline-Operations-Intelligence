import logging
import math

logger = logging.getLogger(__name__)


class ProbabilityCalculator:
    """
    ==========================================================
    Probability Calculator

    Responsibility:
        Convert a 0-100 Risk Score into a smooth 0-100 Risk
        Probability using a logistic sigmoid function, rather
        than hard threshold buckets.

            probability = 100 / (1 + e^(-steepness * (score - midpoint) / 100))

    Input:
        Risk Score

    Output:
        Risk Probability (0-100)

    DOES NOT
    --------
    - Calculate the Risk Score itself
    - Classify severity
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        probability_config = self.rule_engine.get_probability_config()

        self.midpoint = probability_config.get("midpoint", 50)

        self.steepness = probability_config.get("steepness", 8)

        logger.info("Probability Calculator Ready.")

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, risk_score):

        exponent = -self.steepness * (risk_score - self.midpoint) / 100

        probability = 100 / (1 + math.exp(exponent))

        return round(probability, 2)
