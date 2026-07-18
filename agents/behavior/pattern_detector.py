import logging

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    ==========================================================
    Pattern Detector

    Responsibility:
        Detect behavior patterns that only emerge across
        multiple metrics, by counting how many metrics
        crossed a given severity level — never by naming
        specific metrics.

    Input:
        Deviation Analysis Dictionary

    Output:
        List of Detected Pattern Names

    DOES NOT
    --------
    - Compute deviation itself
    - Detect drift across observations
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        self.pattern_rules = self.rule_engine.get_pattern_rules()

        self.severity_order = self.rule_engine.get_severity_order()

        logger.info("Pattern Detector Ready.")

    # =====================================================
    # COUNT BY SEVERITY
    # =====================================================

    def count_by_severity(self, deviation_analysis, severity):

        return sum(

            1 for result in deviation_analysis.values()

            if result["severity"] == severity

        )

    # =====================================================
    # DETECT
    # =====================================================

    def detect(self, deviation_analysis):

        patterns = []

        if not deviation_analysis:

            return patterns

        multi_metric_rule = self.pattern_rules.get(
            "multi_metric_anomaly", {}
        )

        critical_severity = self.severity_order[-1]

        critical_count = self.count_by_severity(
            deviation_analysis, critical_severity
        )

        if critical_count >= multi_metric_rule.get(
            "minimum_critical_metrics", 2
        ):

            patterns.append(

                multi_metric_rule.get(
                    "pattern_name",
                    "Multi-Metric Critical Deviation"
                )

            )

        sustained_warning_rule = self.pattern_rules.get(
            "sustained_warning", {}
        )

        warning_severity = self.severity_order[-2] if len(self.severity_order) > 1 else critical_severity

        warning_count = self.count_by_severity(
            deviation_analysis, warning_severity
        )

        if warning_count >= sustained_warning_rule.get(
            "minimum_warning_metrics", 3
        ):

            patterns.append(

                sustained_warning_rule.get(
                    "pattern_name",
                    "Widespread Warning-Level Deviation"
                )

            )

        if not patterns and (critical_count + warning_count) == 1:

            isolated_rule = self.pattern_rules.get(
                "isolated_anomaly", {}
            )

            patterns.append(

                isolated_rule.get(
                    "pattern_name",
                    "Isolated Metric Anomaly"
                )

            )

        return patterns
