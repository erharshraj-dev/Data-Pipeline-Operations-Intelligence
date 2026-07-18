import logging

logger = logging.getLogger(__name__)


class DeviationAnalyzer:
    """
    ==========================================================
    Deviation Analyzer

    Responsibility:
        Compute percentage deviation between current attribute
        values and historical baseline values, for every
        metric named in the Behavior Rule Engine's
        metric_baseline_map. Reads directly from
        entity["attributes"] and
        entity["context"]["historical_context"], so it works
        for however many or few metrics are actually present
        on a given entity.

    Input:
        Operational Entity

    Output:
        Deviation Analysis Dictionary

    DOES NOT
    --------
    - Detect drift across observations
    - Detect behavior patterns
    - Calculate Behavior Score
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine, severity_classifier):

        self.rule_engine = rule_engine

        self.severity_classifier = severity_classifier

        logger.info("Deviation Analyzer Ready.")

    # =====================================================
    # SAFE DEVIATION CALCULATION
    # =====================================================

    def calculate_deviation(self, current, baseline):

        if baseline in (None, 0):

            return None

        return round(((current - baseline) / baseline) * 100, 2)

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(self, entity):

        attributes = entity.get("attributes", {})

        historical_context = entity.get(
            "context", {}
        ).get(
            "historical_context", {}
        )

        metric_baseline_map = self.rule_engine.get_metric_baseline_map()

        analysis = {}

        for metric_name, baseline_field in metric_baseline_map.items():

            current_value = attributes.get(metric_name)

            baseline_value = historical_context.get(baseline_field)

            if current_value is None or baseline_value is None:

                continue

            deviation = self.calculate_deviation(
                current_value,
                baseline_value
            )

            severity = self.severity_classifier.classify(deviation)

            analysis[metric_name] = {

                "current": current_value,

                "baseline": baseline_value,

                "deviation_percent": deviation,

                "severity": severity

            }

        return analysis
