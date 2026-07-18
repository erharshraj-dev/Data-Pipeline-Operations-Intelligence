import logging

logger = logging.getLogger(__name__)


class BaselineManager:
    """
    ==========================================================
    Baseline Manager

    Responsibility:
        Maintain a small in-memory rolling history of recent
        deviations per entity, per metric, so drift and
        behavioral pattern detection can look across multiple
        observations instead of judging from a single
        snapshot.

    Input:
        Entity ID, Metric Name, Deviation Percentage, Severity

    Output:
        Rolling Deviation History

    DOES NOT
    --------
    - Persist history to disk or database
    - Perform drift detection itself
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        self.history = []

        drift_config = self.rule_engine.get_drift_config()

        self.window_size = drift_config["rolling_window_size"]

        logger.info("Baseline Manager Ready.")

    # =====================================================
    # RECORD
    # =====================================================

    def record(self, entity_id, metric_name, deviation_percent, severity):

        self.history.append({

            "entity_id": entity_id,

            "metric_name": metric_name,

            "deviation_percent": deviation_percent,

            "severity": severity

        })

        while len(self.get_history(entity_id, metric_name)) > self.window_size:

            for index, entry in enumerate(self.history):

                if (
                    entry["entity_id"] == entity_id and
                    entry["metric_name"] == metric_name
                ):

                    del self.history[index]

                    break

    # =====================================================
    # GET HISTORY
    # =====================================================

    def get_history(self, entity_id, metric_name):

        return [
            entry for entry in self.history
            if entry["entity_id"] == entity_id and
            entry["metric_name"] == metric_name
        ]

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        logger.info("Baseline Manager Ready.")

        return True
