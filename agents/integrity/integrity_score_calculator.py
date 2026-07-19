import logging

logger = logging.getLogger(__name__)


class IntegrityScoreCalculator:
    """
    ==========================================================
    Integrity Score Calculator

    Responsibility:
        Combine the five per-check scores into a single 0-100
        Integrity Score using configured weights:

            IntegrityScore = Sum(check_score * weight)

        A check that came back NOT_EVALUATED (no data source
        available for this entity — see record_count.fields in
        integrity_rules.yaml) is excluded and the remaining
        weights are re-normalized, the same missing-signal
        handling risk_score_calculator.py already uses, so an
        unavailable check never silently drags the score down.

    Input:
        Validation Results Dictionary (from Integrity Validator)

    Output:
        Integrity Score (0-100)

    DOES NOT
    --------
    - Run any validation
    - Classify status or trust level
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Integrity Score Calculator Ready.")

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(self, validation_results):

        weights = self.rule_engine.get_weights()

        weighted_sum = 0.0

        total_weight = 0.0

        for check_name, result in validation_results.items():

            if result.get("score") is None:

                continue

            weight = weights.get(check_name, 0.0)

            weighted_sum += result["score"] * weight

            total_weight += weight

        if total_weight == 0:

            return 0.0

        return round(weighted_sum / total_weight, 2)
