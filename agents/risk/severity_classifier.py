import logging

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """
    ==========================================================
    Severity Classifier

    Responsibility:
        Convert a 0-100 Risk Score into a severity label and
        a coarse risk category, using thresholds and mappings
        supplied by the Risk Rule Engine.

    Input:
        Risk Score

    Output:
        Risk Severity Label, Risk Category

    DOES NOT
    --------
    - Calculate the Risk Score itself
    - Calculate probability or confidence
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Severity Classifier Ready.")

    # =====================================================
    # CLASSIFY
    # =====================================================

    def classify(self, risk_score):

        thresholds = self.rule_engine.get_severity_thresholds()

        low_max = thresholds.get("low_max", 25)

        medium_max = thresholds.get("medium_max", 50)

        high_max = thresholds.get("high_max", 75)

        if risk_score <= low_max:

            return "LOW"

        elif risk_score <= medium_max:

            return "MEDIUM"

        elif risk_score <= high_max:

            return "HIGH"

        else:

            return "CRITICAL"

    # =====================================================
    # CATEGORIZE
    # =====================================================

    def categorize(self, severity):

        category_mapping = self.rule_engine.get_category_mapping()

        return category_mapping.get(severity, "Unknown")
