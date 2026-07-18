import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    ==========================================================
    Drift Detector

    Responsibility:
        Determine whether a metric is genuinely drifting,
        using the rolling deviation history maintained by the
        Baseline Manager. A single bad reading is not drift —
        a worsening trend sustained across several recent
        observations is.

    Input:
        Entity ID, Deviation Analysis Dictionary

    Output:
        Drift Analysis Dictionary

    DOES NOT
    --------
    - Compute deviation itself
    - Detect behavior patterns
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine, baseline_manager):

        self.rule_engine = rule_engine

        self.baseline_manager = baseline_manager

        drift_config = self.rule_engine.get_drift_config()

        self.minimum_occurrences = drift_config[
            "sustained_drift_minimum_occurrences"
        ]

        self.drift_severity_levels = drift_config["drift_severity_levels"]

        logger.info("Drift Detector Ready.")

    # =====================================================
    # DETECT
    # =====================================================

    def detect(self, entity_id, deviation_analysis):

        drift_results = {}

        for metric_name, result in deviation_analysis.items():

            severity = result["severity"]

            self.baseline_manager.record(

                entity_id,

                metric_name,

                result["deviation_percent"],

                severity

            )

            history = self.baseline_manager.get_history(
                entity_id, metric_name
            )

            occurrences = sum(

                1 for entry in history

                if entry["severity"] in self.drift_severity_levels

            )

            is_drifting = occurrences >= self.minimum_occurrences

            drift_results[metric_name] = {

                "is_drifting": is_drifting,

                "occurrences": occurrences,

                "observations_tracked": len(history)

            }

        return drift_results
