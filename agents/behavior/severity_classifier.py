import logging

logger = logging.getLogger(__name__)


class SeverityClassifier:
    """
    ==========================================================
    Severity Classifier

    Responsibility:
        Turn a deviation percentage into a severity label,
        using thresholds supplied by the Behavior Rule Engine.

    Input:
        Deviation Percentage

    Output:
        Severity Label
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

    def classify(self, deviation_percent):

        if deviation_percent is None:

            return "UNKNOWN"

        thresholds = self.rule_engine.get_severity_thresholds()

        normal_max = thresholds["normal_max"]

        warning_max = thresholds["warning_max"]

        deviation = abs(deviation_percent)

        if deviation <= normal_max:

            return "NORMAL"

        elif deviation <= warning_max:

            return "WARNING"

        else:

            return "CRITICAL"

    # =====================================================
    # SCORE
    # =====================================================

    def score(self, severity):

        return self.rule_engine.get_severity_score(severity)
