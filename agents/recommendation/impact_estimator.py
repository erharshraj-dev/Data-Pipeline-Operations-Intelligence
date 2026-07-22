import logging

logger = logging.getLogger(__name__)


class ImpactEstimator:
    """
    ==========================================================
    Impact Estimator

    Responsibility:
        Estimate Expected Impact, Estimated Recovery Time,
        Automation Possible, and Human Approval Required for a
        given priority and recommendation context — every
        mapping and rule read from recommendation_rules.yaml,
        nothing hardcoded.

    Input:
        Priority Label, Recommendation Context Dictionary

    Output:
        Impact Estimate Dictionary

    DOES NOT
    --------
    - Calculate priority
    - Retrieve knowledge
    - Call Gemini
    ==========================================================
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, rule_engine):

        self.rule_engine = rule_engine

        logger.info("Impact Estimator Ready.")

    # =====================================================
    # EXPECTED IMPACT
    # =====================================================

    def estimate_expected_impact(self, priority):

        impact_mapping = self.rule_engine.get_impact_mapping()

        return impact_mapping.get(priority)

    # =====================================================
    # ESTIMATED RECOVERY TIME
    # =====================================================

    def estimate_recovery_time(self, priority):

        recovery_time_mapping = self.rule_engine.get_recovery_time_mapping()

        return recovery_time_mapping.get(priority)

    # =====================================================
    # AUTOMATION POSSIBLE
    # =====================================================

    def estimate_automation_possible(self, priority, context):

        automation_rules = self.rule_engine.get_automation_rules()

        automatable_priorities = automation_rules.get(
            "automatable_priorities", []
        )

        automatable_categories = automation_rules.get(
            "automatable_categories", []
        )

        default_automation_possible = automation_rules.get(
            "default_automation_possible", False
        )

        if not automatable_priorities and not automatable_categories:

            return default_automation_possible

        priority_ok = (
            not automatable_priorities
            or priority in automatable_priorities
        )

        category_ok = (
            not automatable_categories
            or context.get("risk_category") in automatable_categories
        )

        return priority_ok and category_ok

    # =====================================================
    # HUMAN APPROVAL REQUIRED
    # =====================================================

    def estimate_human_approval_required(self, priority, context):

        human_approval_rules = self.rule_engine.get_human_approval_rules()

        requires_approval_priorities = human_approval_rules.get(
            "requires_approval_priorities", []
        )

        requires_approval_categories = human_approval_rules.get(
            "requires_approval_categories", []
        )

        default_human_approval_required = human_approval_rules.get(
            "default_human_approval_required", True
        )

        if (
            priority in requires_approval_priorities
            or context.get("risk_category") in requires_approval_categories
        ):

            return True

        if not requires_approval_priorities and not requires_approval_categories:

            return default_human_approval_required

        return False

    # =====================================================
    # ESTIMATE ALL
    # =====================================================

    def estimate(self, priority, context):

        return {

            "expected_impact": self.estimate_expected_impact(priority),

            "estimated_recovery_time": self.estimate_recovery_time(
                priority
            ),

            "automation_possible": self.estimate_automation_possible(
                priority, context
            ),

            "human_approval_required":
                self.estimate_human_approval_required(priority, context)

        }
