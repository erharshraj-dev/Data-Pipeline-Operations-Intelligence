import logging

logger = logging.getLogger(__name__)


class IntegrityStatusClassifier:
    """
    ==========================================================
    Integrity Status Classifier

    Responsibility:
        Convert the 0-100 Integrity Score into an Integrity
        Status (PASS / WARNING / FAILED) and an Output Trust
        Level (HIGH / MEDIUM / LOW), using thresholds from the
        Rule Engine. Also determines the Primary Failure
        Reason — the highest-priority FAILED check, or failing
        that the highest-priority WARNING check, or "None".

    Input:
        Integrity Score, Validation Results Dictionary

    Output:
        Integrity Status, Output Trust Level, Primary Failure
        Reason

    DOES NOT
    --------
    - Calculate the Integrity Score itself
    - Run any validation
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Integrity Status Classifier Ready.")

    # =====================================================
    # CLASSIFY STATUS
    # =====================================================

    def classify_status(self, integrity_score):

        thresholds = self.rule_engine.get_status_thresholds()

        pass_min = thresholds.get("pass_min", 90)

        warning_min = thresholds.get("warning_min", 70)

        if integrity_score >= pass_min:

            return "PASS"

        elif integrity_score >= warning_min:

            return "WARNING"

        else:

            return "FAILED"

    # =====================================================
    # CLASSIFY TRUST LEVEL
    # =====================================================

    def classify_trust_level(self, integrity_score):

        thresholds = self.rule_engine.get_trust_level_thresholds()

        high_min = thresholds.get("high_min", 90)

        medium_min = thresholds.get("medium_min", 70)

        if integrity_score >= high_min:

            return "HIGH"

        elif integrity_score >= medium_min:

            return "MEDIUM"

        else:

            return "LOW"

    # =====================================================
    # PRIMARY FAILURE REASON
    # =====================================================

    def determine_primary_failure(self, validation_results):

        priority = self.rule_engine.get_validation_priority()

        ranked_checks = sorted(

            validation_results.keys(),

            key=lambda check_name: priority.get(check_name, 0),

            reverse=True

        )

        for target_status in ("FAILED", "WARNING"):

            for check_name in ranked_checks:

                if validation_results[check_name]["status"] == target_status:

                    return self.rule_engine.get_check_display_name(
                        check_name
                    )

        return "None"
