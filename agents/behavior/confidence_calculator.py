import logging

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """
    ==========================================================
    Confidence Calculator

    Responsibility:
        Calculate how much to trust the Behavior Score for a
        given entity, based on how many metrics were actually
        analyzable and how complete the entity's historical
        context was — an explainable, config-driven
        calculation, not a guess.

    Input:
        Operational Entity, Deviation Analysis Dictionary

    Output:
        Confidence Score (0.0 - 1.0)
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

    def calculate(self, entity, deviation_analysis):

        max_expected_metrics = self.confidence_config["max_expected_metrics"]

        metric_coverage_weight = self.confidence_config[
            "metric_coverage_weight"
        ]

        context_completeness_weight = self.confidence_config[
            "context_completeness_weight"
        ]

        minimum_confidence = self.confidence_config["minimum_confidence"]

        maximum_confidence = self.confidence_config["maximum_confidence"]

        analyzable_metrics = len(deviation_analysis)

        if max_expected_metrics > 0:

            metric_coverage = min(
                analyzable_metrics / max_expected_metrics, 1.0
            )

        else:

            metric_coverage = 0.0

        historical_context = entity.get(
            "context", {}
        ).get(
            "historical_context", {}
        )

        context_completeness = 1.0 if historical_context else 0.0

        confidence = (

            (metric_coverage * metric_coverage_weight) +

            (context_completeness * context_completeness_weight)

        )

        confidence = max(

            minimum_confidence,

            min(confidence, maximum_confidence)

        )

        return round(confidence, 2)
