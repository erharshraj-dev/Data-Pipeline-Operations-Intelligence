import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrityObjectBuilder:
    """
    -------------------------------------------------------
    Integrity Object Builder

    Responsibility:
    Build the final Integrity Object from the Integrity
    Agent's validation outputs.

    Input:
        Observation Object
        Validation Results Dictionary
        Integrity Score, Integrity Status, Output Trust Level,
        Primary Failure Reason, Execution Time (ms)

    Output:
        Integrity Object

    NOTE:
        validation_summary and validation_details are both
        small presentational rollups computed here over
        validation_results, which validate_all() already
        produced — neither is a new validation decision.
        validation_summary is aggregate counts
        (passed/warning/failed/not_evaluated); validation_
        details is a per-check {status, message} view aimed at
        downstream consumers like the Recommendation Agent
        that want a flat status per check without the score.
    -------------------------------------------------------
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, agent_version="1.0"):

        # agent_version now comes from integrity_rules.yaml via
        # IntegrityRuleEngine.get_agent_version(), passed in by
        # IntegrityAgent at construction time, rather than being
        # hardcoded here.

        self.agent_version = agent_version

        logger.info("Integrity Object Builder Ready.")

    # =====================================================
    # VALIDATION SUMMARY
    # =====================================================

    def build_validation_summary(self, validation_results):

        summary = {

            "total_checks": len(validation_results),
            "passed": 0,
            "warning": 0,
            "failed": 0,
            "not_evaluated": 0

        }

        status_key_map = {

            "PASS": "passed",
            "WARNING": "warning",
            "FAILED": "failed",
            "NOT_EVALUATED": "not_evaluated"

        }

        for result in validation_results.values():

            key = status_key_map.get(result["status"])

            if key:

                summary[key] += 1

        return summary

    # =====================================================
    # VALIDATION DETAILS
    #
    # Per-check {status, message} view, e.g.:
    #   schema:
    #     status: FAILED
    #     message: "Missing: customer_id"
    # Reshapes validation_results (which also carries "score")
    # into the flatter, message-oriented shape downstream
    # consumers like the Recommendation Agent expect.
    # =====================================================

    def build_validation_details(self, validation_results):

        return {

            check_name: {

                "status": result.get("status"),

                "message": result.get("details")

            }

            for check_name, result in validation_results.items()

        }

    # =====================================================
    # BUILD INTEGRITY OBJECT
    # =====================================================

    def build(
        self,
        observation_object,
        validation_results,
        integrity_score,
        integrity_status,
        output_trust_level,
        primary_failure_reason,
        execution_time_ms
    ):

        integrity_object = {

            "entity_id": observation_object.get("entity_id"),

            "integrity_score": integrity_score,

            "integrity_status": integrity_status,

            "output_trust_level": output_trust_level,

            "validation_summary": self.build_validation_summary(
                validation_results
            ),

            "validation_results": validation_results,

            "validation_details": self.build_validation_details(
                validation_results
            ),

            "primary_failure_reason": primary_failure_reason,

            "execution_time_ms": execution_time_ms,

            "evaluation_timestamp": datetime.now().isoformat(),

            "agent_version": self.agent_version

        }

        return integrity_object
