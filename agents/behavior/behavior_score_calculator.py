import logging

logger = logging.getLogger(__name__)


class BehaviorScoreCalculator:
    """
    ==========================================================
    Behavior Score Calculator

    Responsibility:
        Combine every metric's individual severity into one
        overall 0-100 Behavior Score, using whichever
        aggregation strategy is configured — never a
        hardcoded formula.

    Input:
        Deviation Analysis Dictionary

    Output:
        Behavior Score (float)

    DOES NOT
    --------
    - Classify severity
    - Determine confidence
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine, severity_classifier):

        self.rule_engine = rule_engine

        self.severity_classifier = severity_classifier

        self.behavior_score_config = (
            self.rule_engine.get_behavior_score_config()
        )

        self.aggregation_strategy = self.behavior_score_config[
            "aggregation_strategy"
        ]

        logger.info("Behavior Score Calculator Ready.")

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, deviation_analysis):

        if not deviation_analysis:

            return 0.0

        scores = []

        weights = []

        for metric_name, result in deviation_analysis.items():

            severity_score = self.severity_classifier.score(
                result["severity"]
            )

            weight = self.rule_engine.get_metric_weight(metric_name)

            scores.append(severity_score)

            weights.append(weight)

        if self.aggregation_strategy == "max":

            return float(max(scores))

        elif self.aggregation_strategy == "average":

            return round(sum(scores) / len(scores), 2)

        else:

            weighted_sum = sum(

                score * weight

                for score, weight in zip(scores, weights)

            )

            total_weight = sum(weights)

            if total_weight == 0:

                return 0.0

            return round(weighted_sum / total_weight, 2)
